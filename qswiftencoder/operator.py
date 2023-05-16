from abc import ABC


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


class MultiSwiftOperator(Operator):
    def __init__(self, jvec, bvec):
        self.jvec = jvec
        self.bvec = bvec

    def __repr__(self):
        results = []
        for j, b in zip(self.jvec, self.bvec):
            results.append(f"S{j}-{b}")
        return " ".join(results)


class MeasurementOperator(Operator):
    def __init__(self, j):
        self.j = j

    def __repr__(self):
        return f"M{self.j}"
