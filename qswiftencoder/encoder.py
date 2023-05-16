import collections.abc
from abc import ABC
from qwrapper.circuit import QWrapper
from qwrapper.operator import PauliTimeEvolution, PauliObservable


class Operator(ABC):
    pass


class TimeOperator(Operator):
    def __init__(self, j):
        self.j = j

    def __repr__(self) -> str:
        return "T" + str(self.j)


class SwiftOperator(Operator):
    def __init__(self, j, b):
        self.j = j
        self.b = b

    def __repr__(self):
        return f"S{self.j}:{self.b}"


class LOperator(Operator):
    def __init__(self, j):
        self.j = j

    def __repr__(self):
        return f"L{self.j}"


class MeasurementOperator(Operator):
    def __init__(self, j):
        self.j = j

    def __repr__(self):
        return f"M{self.j}"


class SwiftChannels:
    def __init__(self, coeff):
        self.coeff = coeff
        self.operators = []
        self.measurement = None

    def add_time_operator(self, j):
        self.operators.append(TimeOperator(j))

    def add_time_operators(self, array):
        for j in array:
            self.add_time_operator(j)

    def add_l_operator(self, j):
        self.operators.append(LOperator(j))

    def set_measurement_operator(self, j):
        self.measurement = MeasurementOperator(j)


class QSwiftImplementableEncoder:
    def encode(self, channels: SwiftChannels) -> [[Operator]]:
        results = self.do_encode([], channels.operators)
        if channels.measurement is not None:
            for operators in results:
                operators.append(channels.measurement)
        return results

    def do_encode(self, current, operators):
        results = []
        result = current
        for j, o in enumerate(operators):
            if isinstance(o, LOperator):
                r1 = result.copy()
                r2 = result.copy()
                r1.append(SwiftOperator(o.j, b=0))
                r2.append(SwiftOperator(o.j, b=1))
                results.extend(self.do_encode(r1, operators[j + 1:]))
                results.extend(self.do_encode(r2, operators[j + 1:]))
                return results
            result.append(o)
        return [result]


class QSwiftStringEncoder:
    def encode(self, coeff, operators):
        res = [str(coeff)]
        for o in operators:
            if isinstance(o, LOperator):
                raise AttributeError("L Operator is not implementable.")
            res.append(str(o))
        return " ".join(res)


class QSwiftCircuitExecutor:
    def __init__(self, paulis, observables, tau):
        if isinstance(paulis, collections.abc.Sequence):
            map = {}
            for j, pauli in enumerate(paulis):
                map[j] = pauli
            paulis = map
        if isinstance(observables, collections.abc.Sequence):
            map = {}
            for j, pauli in enumerate(paulis):
                map[j] = pauli
            observables = map
        self._paulis = paulis
        self._observables = observables
        self._tau = tau
        self._cache = {}

    def compute(self, qc: QWrapper, code, nshot=0):
        operators = []
        ancilla_index = qc.nqubit
        targets = [j for j in qc.nqubit]
        items = code.split(" ")
        coeff = float(items[0])
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
                return coeff * self._observables[operator.j].get_value(qc, nshot)
        raise AttributeError("measurement is not set")

    def add_gate(self, qc: QWrapper, operator: Operator, tau, ancilla_index, targets):
        if isinstance(operator, SwiftOperator):
            qc.s(ancilla_index)
            pauli = self._paulis[operator.j]
            if pauli.sign == -1:
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
    def __init__(self, *, operators, observables, tau):
        self.implementable_encoder = QSwiftImplementableEncoder()
        self.string_encoder = QSwiftStringEncoder()
        self.circuit_encoder = QSwiftCircuitExecutor(operators, observables, tau)

    def to_strings(self, swift_channels: SwiftChannels):
        operators_array = self.implementable_encoder.encode(swift_channels)
        results = []
        for operators in operators_array:
            results.append(self.string_encoder.encode(swift_channels.coeff, operators))
        return results

    def execute(self, qc: QWrapper, code, nshot):
        return self.circuit_encoder.compute(qc, code, nshot)
