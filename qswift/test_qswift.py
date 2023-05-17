from unittest import TestCase
import logging, numpy as np
from qwrapper.hamiltonian import Hamiltonian, to_matrix_hamiltonian
from qwrapper.obs import PauliObservable
from benchmark.molecule import MolecularHamiltonian
from qswift.initializer import XBasisInitializer, CircuitInitializer
from qswift.qswift import QSwift
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


class TestQSwift(TestCase):
    def test_qswift(self):
        logging.getLogger().setLevel(level=logging.INFO)
        obs = Hamiltonian([1], [PauliObservable("ZIIIIIII")], 8)
        hamiltonian = MolecularHamiltonian(8, "6-31g", "hydrogen")
        initializer = XBasisInitializer()
        t = 10
        N = 1000

        exact = ExactComputation(to_matrix_hamiltonian(obs),
                                 to_matrix_hamiltonian(hamiltonian), t, initializer)
        ex = exact.compute()

        qswift = QSwift(hamiltonian, obs, initializer, t=t, N=N, K=2, nshot=10, n_p=10000)
        print(ex, qswift.evaluate().sum(0), qswift.evaluate().sum(1), qswift.evaluate().sum(2))
