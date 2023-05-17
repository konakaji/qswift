import collections.abc
import random
from qwrapper.circuit import QWrapper
from qwrapper.operator import PauliTimeEvolution, PauliObservable
from qwrapper.sampler import ImportantSampler
from qswift.operator import *
from qswift.initializer import CircuitInitializer


class MultiIndexSampler:
    def __init__(self, sampler: ImportantSampler):
        self.sampler = sampler

    def sample(self, s, n):
        if s == 0:
            return self.sampler.sample_indices(count=n)
        elif s == 1:
            index = self.sampler.sample_index()
            return [index for _ in range(n)]
        else:
            raise AttributeError("illegal s value.")


class SwiftChannel:
    def __init__(self, coeff):
        self.coeff = coeff
        self.operators = []
        self.measurement = None

    def add_time_operator(self, j):
        self.operators.append(TimeOperator(j))

    def add_time_operators(self, array):
        for j in array:
            self.add_time_operator(j)

    def add_swift_operator(self, j, b):
        self.operators.append(SwiftOperator(j, b))

    def add_multi_swift_operators(self, j_vec, b_vec):
        self.operators.append(MultiSwiftOperator(j_vec, b_vec))

    def shuffle(self, seed):
        random.Random(seed).shuffle(self.operators)

    def set_measurement_operator(self, j):
        self.measurement = MeasurementOperator(j)


class QSwiftStringEncoder:
    def encode(self, swift_channel: SwiftChannel):
        res = [str(swift_channel.coeff)]
        for o in swift_channel.operators:
            res.append(str(o))
        res.append(str(swift_channel.measurement))
        return " ".join(res)


class QSwiftCircuitExecutor:
    def __init__(self, paulis, observables, initializer: CircuitInitializer, tau, nshot=0, tool="qulacs"):
        if isinstance(paulis, collections.abc.Sequence):
            map = {}
            for j, pauli in enumerate(paulis):
                map[j] = pauli
            paulis = map
        if isinstance(observables, collections.abc.Sequence):
            map = {}
            for j, obs in enumerate(observables):
                map[j] = obs
            observables = map
        obs_map = {}
        for k, obs in observables.items():
            obs_map[k] = PauliObservable(obs.p_string + "X", obs.sign)
        self._initializer = initializer
        self._paulis = paulis
        self._observables = obs_map
        self._tau = tau
        self._cache = {}
        self._nqubit = list(self._observables.values())[0].nqubit
        self._nshot = nshot
        self._tool = tool

    def compute(self, code):
        ancilla_index = self._nqubit - 1
        qc = self._initializer.init_circuit(self._nqubit, {ancilla_index}, self._tool)
        operators = []
        targets = [j for j in range(self._nqubit - 1)]
        items = code.split(" ")
        coeff = float(items[0])
        qc.h(ancilla_index)
        for s in items[1:]:
            if s.startswith("T"):
                operators.append(TimeOperator(int(s[1:])))
            elif s.startswith("S"):
                j, b = s[1:].split(":")
                operators.append(SwiftOperator(int(j), int(b)))
            elif s.startswith("M"):
                operators.append(MeasurementOperator(int(s[1:])))
        for operator in operators:
            self.add_gate(qc, operator, self._tau, ancilla_index, targets)
            if isinstance(operator, MeasurementOperator):
                value = coeff * self._observables[operator.j].get_value(qc, self._nshot)
                qc.draw_and_show()
                return value
        raise AttributeError("measurement is not set")

    def add_gate(self, qc: QWrapper, operator: Operator, tau, ancilla_index, targets):
        if isinstance(operator, SwiftOperator):
            qc.s(ancilla_index)
            pauli = self._paulis[operator.j]
            if pauli._sign == -1:
                qc.z(ancilla_index)
            if operator.b == 0:
                qc.z(ancilla_index)
                qc.x(ancilla_index)
                pauli.add_controlled_circuit(ancilla_index, targets, qc)
                qc.x(ancilla_index)
            else:
                pauli.add_controlled_circuit(ancilla_index, targets, qc)
        elif isinstance(operator, TimeOperator):
            if operator.j not in self._cache:
                self._cache[operator.j] = PauliTimeEvolution(self._paulis[operator.j], tau)
            self._cache[operator.j].add_circuit(qc)


class Compiler:
    def __init__(self, *, operators, observables, initializer, tau, nshot=0, tool="qulacs"):
        self.string_encoder = QSwiftStringEncoder()
        self.circuit_encoder = QSwiftCircuitExecutor(operators, observables, initializer, tau, nshot, tool)
        self.initializer = initializer

    def to_string(self, swift_channel: SwiftChannel):
        return self.string_encoder.encode(swift_channel)

    def evaluate(self, code):
        return self.circuit_encoder.compute(code)
