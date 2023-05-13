from abc import ABC
from qwrapper.circuit import QWrapper
from qwrapper.operator import PauliTimeEvolution


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
        return f"S{self.j}-{self.b}"


class QSwiftStringEncoder:
    def encode(self, coeff, operators):
        res = [str(coeff)]
        for o in operators:
            res.append(str(o))
        return " ".join(res)


class QSwiftCircuitEncoder:
    def __init__(self, ancilla_index, targets, paulis, tau):
        self._ancilla_index = ancilla_index
        self._targets = targets
        self._paulis = paulis
        self._tau = tau
        self._cache = {}

    def encode(self, qc: QWrapper, code):
        operators = []
        items = code.split(" ")
        coeff = float(items[0])
        for s in items[1:]:
            if s.startswith("T"):
                operators.append(TimeOperator(int(s[1:])))
            elif s.startswith("S"):
                j, b = s[1:].split("-")
                operators.append(SwiftOperator(int(j), int(b)))
        for operator in operators:
            self.add_gate(qc, operator, self._tau)
        return coeff, qc

    def add_gate(self, qc: QWrapper, operator: Operator, tau):
        if isinstance(operator, SwiftOperator):
            qc.s(self._ancilla_index)
            pauli = self._paulis[operator.j]
            if pauli.sign == -1:
                qc.z(self._ancilla_index)
            if operator.b == 0:
                qc.z(self._ancilla_index)
                qc.x(self._ancilla_index)
                pauli.add_controlled_circuit(self._ancilla_index, self._targets, qc)
                qc.x(self._ancilla_index)
            else:
                pauli.add_controlled_circuit(self._ancilla_index, self._targets, qc)
        elif isinstance(operator, TimeOperator):
            if operator.j not in self._cache:
                self._cache[operator.j] = PauliTimeEvolution(self._paulis[operator.j], tau)
            self._cache[operator.j].add_circuit(qc)
