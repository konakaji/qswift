import math, logging
from qwrapper.obs import Hamiltonian
from qwrapper.sampler import ImportantSampler, FasterImportantSampler
from qswift.compiler import Compiler, OperatorPool, DefaultOperatorPool
from qswift.executor import QSwiftExecutor, ThreadPoolQSwiftExecutor
from qswift.initializer import CircuitInitializer
from qswift.measurement import NaiveGenerator
from qswift.metric import QSwiftResult
from qswift.sampler import QSwiftSampler
from qswift.util import binom, all_combinations, make_positive


class QSwift:
    def __init__(self, observable: Hamiltonian, initializer: CircuitInitializer,
                 *, t, N, K, n_p, max_workers=1,
                 chunk_size=1000, nshot=0, tool="qulacs"):
        """
        :param observable: observable
        :param initializer: circuit initialization
        :param t: time
        :param N: # of time evolution steps
        :param K: order-parameter
        :param n_p:
        :param nshot: number of shots
        :param tool qulacs or qiskit
        :param max_workers:
        """
        self.logger = logging.getLogger("qswift.qswift.QSwift")
        self.initializer = initializer
        self.observable = make_positive(observable).gen_ancilla_hamiltonian("X")
        self.t = t
        self.nshot = nshot
        self.tool = tool
        if max_workers == 1:
            self.executor = QSwiftExecutor()
        else:
            self.executor = ThreadPoolQSwiftExecutor(max_workers, chunk_size)
        self.N = N
        self.K = K
        self.n_p = n_p
        self.max_workers = max_workers
        self.chunk_size = chunk_size

    def evaluate(self, hamiltonian: Hamiltonian = None, sampler: ImportantSampler = None,
                 operator_pool: OperatorPool = None, lam=None) -> QSwiftResult:
        """
        Either hamiltonian or (sampler, operator_pool, lam) must be specified
        """
        if hamiltonian is not None:
            assert sampler is None
            assert operator_pool is None
            assert lam is None
            hamiltonian = make_positive(hamiltonian)
            sampler = FasterImportantSampler(hamiltonian.hs)
            operator_pool = DefaultOperatorPool(hamiltonian.paulis)
            lam = hamiltonian.lam()
        else:
            assert sampler is not None
            assert operator_pool is not None
            assert lam is not None
        tau = lam * self.t / self.N

        if self.nshot == 0:
            compiler = Compiler(operator_pool=operator_pool,
                                observables=[self.observable],
                                initializer=self.initializer,
                                tau=tau, nshot=self.nshot, tool=self.tool)
            mes_generator = NaiveGenerator([1])
        else:
            compiler = Compiler(operator_pool=operator_pool,
                                observables=self.observable.paulis,
                                initializer=self.initializer,
                                tau=tau, nshot=self.nshot, tool=self.tool)
            mes_generator = NaiveGenerator(self.observable.hs)
        return self.do_evaluate(sampler, compiler, mes_generator, tau)

    def do_evaluate(self, sampler: ImportantSampler, compiler: Compiler, mes_generator, tau):
        result = QSwiftResult()
        self.logger.info(f"xi:{0}, n_vec:{[]}, coeff:{1}")
        qswift_sampler = QSwiftSampler(0, 0, [], sampler, self.N)
        self.logger.info(f"sampling...")
        swift_channels = qswift_sampler.sample(mes_generator.generate(self.n_p))
        self.logger.info(f"executing...")
        value = self.executor.execute(compiler, swift_channels)
        result.add(0, 0, value)
        self.logger.info(f"value: {value}")
        for xi in range(2, 2 * self.K + 1):
            for k in range(1, self.N + 1):
                if 2 * k > xi:
                    continue
                for n_vec in self._n_vecs(k, xi):
                    coeff = self._coeff(n_vec, k, xi, tau)
                    self.logger.info(f"xi:{xi}, n_vec:{n_vec}, coeff:{coeff}")
                    qswift_sampler = QSwiftSampler(k, xi, n_vec, sampler, self.N)
                    swift_channels = qswift_sampler.sample(mes_generator.generate(math.ceil(self.n_p * coeff)))
                    value = coeff * self.executor.execute(compiler, swift_channels)
                    result.add(xi, k, value)
                    self.logger.info(f"value: {value}")
            if xi % 2 == 0:
                order = int(xi / 2)
                logging.info(f"order: {order} estimate: {result.sum(order)}")
        return result

    def _coeff(self, n_vec, k, xi, tau):
        factor = 1
        for v in n_vec:
            factor = factor * math.factorial(v)
        return binom(self.N, k) * tau ** xi * 1 / factor

    def _n_vecs(self, k, xi):
        for vec in all_combinations(xi, k, 2):
            yield vec
