from qswift.initializer import CircuitInitializer
from scipy.linalg import expm
import numpy as np


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
