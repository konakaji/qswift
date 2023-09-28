import math

from qwrapper.obs import Hamiltonian
from qwrapper.operator import PauliTimeEvolution
from qswift.initializer import CircuitInitializer
from qswift.util import make_positive
from qswift.compiler import OperatorPool


class Sequence:
    def __init__(self, observable: Hamiltonian, initializer: CircuitInitializer, operator_pool: OperatorPool,
                 *, taus, nshot=0, tool="qulacs"):
        """
        :param observable:
        :param initializer:
        :param operator_pool
        :param taus:
        :param nshot:
        :param tool:
        """
        self._cache = {}
        self.initializer = initializer
        self.operator_pool = operator_pool
        self.observable = make_positive(observable)
        self.taus = taus
        self.nshot = nshot
        self.tool = tool

    def evaluate(self, indices):
        if self.nshot == 0:
            return self.observable.exact_value(self.get_circuit(indices))
        res = 0
        for h, p in zip(self.observable.hs, self.observable.paulis):
            res += h * p.get_value(self.get_circuit(indices), self.nshot)
        return res

    def get_circuit(self, indices):
        qc = self.initializer.init_circuit(self.observable.nqubit, {}, self.tool)
        for index in indices:
            operator_index = self.get_operator_index(index)
            operator = self.operator_pool.get(operator_index)
            tau = self.get_tau(index)
            if index not in self._cache:
                self._cache[index] = PauliTimeEvolution(operator, tau, cachable=True)
            self._cache[index].add_circuit(qc)
        return qc

    def get_operator_index(self, index):
        return index % self.operator_pool.size()

    def get_tau(self, index):
        return self.taus[math.floor(index / self.operator_pool.size())]
