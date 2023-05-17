import logging, numpy as np

from qwrapper.hamiltonian import to_matrix_hamiltonian
from qswift.qswift import QSwift
from qswift.initializer import XBasisInitializer, CircuitInitializer
from benchmark.molecule import MolecularHamiltonian
from qwrapper.hamiltonian import Hamiltonian
from qwrapper.obs import PauliObservable

from scipy.linalg import expm


class Channel:
    def __init__(self, m, inv):
        self.m = m
        self.inv = inv

    def apply(self, rho):
        return self.m.dot(rho).dot(self.inv)


class ExactComputation:
    def __init__(self, obs, hamiltonian_matrix, t, initializer: CircuitInitializer):
        self.initializer = initializer
        self.hamiltonian_matrix = hamiltonian_matrix
        self.t = t
        self.obs = obs

    def compute(self):
        channel = Channel(expm(1j * self.hamiltonian_matrix * self.t), expm(-1j * self.hamiltonian_matrix * self.t))
        state = self.initializer.initial_state(len(self.hamiltonian_matrix))
        rho = channel.apply(state)
        return np.trace(rho.dot(self.obs)).real


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    t = 1

    obs = Hamiltonian([1], [PauliObservable("ZIIIIIII")], 8)
    hamiltonian = MolecularHamiltonian(8, "6-31g", "hydrogen")
    initializer = XBasisInitializer()

    exact = ExactComputation(to_matrix_hamiltonian(obs),
                             to_matrix_hamiltonian(hamiltonian), t, initializer)
    ex = exact.compute()
    print(ex)

    N = 200
    qswift = QSwift(hamiltonian, obs, initializer, t=t, N=N, K=2, nshot=100, n_p=10000, tool="qulacs")
    result = qswift.evaluate()
    print(ex, result.sum(0), result.sum(1), result.sum(2))
