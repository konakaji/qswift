import math, logging
from qwrapper.obs import Hamiltonian
from qswiftencoder.compiler import Compiler
from qswiftencoder.executor import QSwiftExecutor, ThreadPoolQSwiftExecutor
from qswiftencoder.initializer import CircuitInitializer
from qswiftencoder.metric import QSwiftResult
from qswiftencoder.sampler import QSwiftSampler
from qswiftencoder.util import binom, all_combinations


class QSwift:
    def __init__(self, hamiltonian: Hamiltonian, observable: Hamiltonian, initializer: CircuitInitializer,
                 *, t, N, K, n_p, max_workers=1,
                 chunk_size=1000, tool="qulacs"):
        """
        :param hamiltonian: evolution Hamiltonian
        :param observable: observable
        :param t: time
        :param N: # of time evolution steps
        :param K: order-parameter
        :param n_p:
        :param max_workers:
        """
        self.hamiltonian = hamiltonian
        self.observable = observable
        self.tau = hamiltonian.lam() * t / N
        compiler = Compiler(operators=hamiltonian.paulis,
                            observables=observable.paulis,
                            initializer=initializer,
                            tau=self.tau, tool=tool)
        if max_workers == 1:
            self.executor = QSwiftExecutor(compiler)
        else:
            self.executor = ThreadPoolQSwiftExecutor(compiler, max_workers, chunk_size)
        self.N = N
        self.K = K
        self.n_p = n_p
        self.max_workers = max_workers
        self.chunk_size = chunk_size

    def evaluate(self) -> QSwiftResult:
        result = QSwiftResult()
        logging.info(f"xi:{0}, n_vec:{[]}, coeff:{1}")
        sampler = QSwiftSampler(0, 0, [], self.hamiltonian.hs, self.observable.hs, self.N)
        swift_channels = sampler.sample(self.n_p)
        value = self.executor.execute(swift_channels)
        result.add(0, 0, value)
        logging.info(f"value: {value}")
        for xi in range(2, 2 * self.K + 1):
            for k in range(1, self.N + 1):
                if 2 * k > xi:
                    continue
                for n_vec in self._n_vecs(k, xi):
                    coeff = self._coeff(n_vec, k, xi)
                    logging.info(f"xi:{xi}, n_vec:{n_vec}, coeff:{coeff}")
                    sampler = QSwiftSampler(k, xi, n_vec, self.hamiltonian.hs, self.observable.hs, self.N)
                    swift_channels = sampler.sample(math.ceil(self.n_p * coeff))
                    value = coeff * self.executor.execute(swift_channels)
                    result.add(xi, k, value)
                    logging.info(f"value: {value}")
            if xi % 2 == 0:
                order = int(xi / 2)
                logging.info(f"order: {order} estimate: {result.sum(order)}")
        return result

    def _coeff(self, n_vec, k, xi):
        factor = 1
        for v in n_vec:
            factor = factor * math.factorial(v)
        return binom(self.N, k) * self.tau ** xi * 1 / factor

    def _n_vecs(self, k, xi):
        for vec in all_combinations(xi, k, 2):
            yield vec
