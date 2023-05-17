from abc import ABC, abstractmethod
from qwrapper.circuit import init_circuit
from qswift.util import zero_state
import numpy as np


class CircuitInitializer(ABC):
    @abstractmethod
    def init_circuit(self, nqubit, ancilla, tool):
        pass

    @abstractmethod
    def initial_state(self, dim):
        pass


class ZBasisInitializer(CircuitInitializer):
    def init_circuit(self, nqubit, ancilla, tool):
        qc = init_circuit(nqubit, tool)
        return qc

    def initial_state(self, dim):
        return zero_state(dim)


class XBasisInitializer(CircuitInitializer):
    def init_circuit(self, nqubit, ancilla: set, tool):
        qc = init_circuit(nqubit, tool)
        for j in range(nqubit):
            if j in ancilla:
                continue
            qc.h(j)
        return qc

    def initial_state(self, dim):
        result = np.diag(np.zeros(dim))
        for i in range(dim):
            for j in range(dim):
                result[i][j] = 1 / dim
        return result
