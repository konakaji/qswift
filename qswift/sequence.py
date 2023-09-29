import math

from qwrapper.obs import Hamiltonian
from qwrapper.operator import PauliTimeEvolution, Operator
from qswift.initializer import CircuitInitializer
from qswift.util import make_positive
from qswift.compiler import OperatorPool
from abc import ABC, abstractmethod


class GeneralPool:
    def get(self, j) -> Operator:
        pass

    def size(self):
        pass


class PauliEvolutionPool(GeneralPool):
    def __init__(self, operator_pool, taus):
        self.operator_pool = operator_pool
        self.taus = taus
        self._cache = {}

    def get(self, j) -> PauliTimeEvolution:
        if j not in self._cache:
            operator_index = self.get_operator_index(j)
            operator = self.operator_pool.get(operator_index)
            tau = self.get_tau(j)
            self._cache[j] = PauliTimeEvolution(operator, tau, cachable=True)
        return self._cache[j]

    def get_operator_index(self, index):
        return index % self.operator_pool.size()

    def get_tau(self, index):
        return self.taus[math.floor(index / self.operator_pool.size())]

    def size(self):
        return self.operator_pool.size() * len(self.taus)


class Sequence:
    def __init__(self, observable: Hamiltonian, initializer: CircuitInitializer,
                 operator_pool=None, taus=None, general_pool=None,
                 *, nshot=0, tool="qulacs"):
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
        assert general_pool is not None or operator_pool is not None
        if operator_pool is not None:
            self.pool: GeneralPool = PauliEvolutionPool(operator_pool, taus)
        else:
            self.pool: GeneralPool = general_pool
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
            self.pool.get(index).add_circuit(qc)
        return qc
