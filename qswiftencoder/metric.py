import sys


class QSwiftResult:
    def __init__(self):
        self.map = {}

    def add(self, xi, k, value):
        if xi not in self.map:
            self.map[xi] = {}
        if k not in self.map[xi]:
            self.map[xi][k] = 0
        self.map[xi][k] += value

    def get(self, xi):
        result = 0
        for v in self.map[xi].values():
            result += v
        return result

    def sum_list(self, order_max):
        values = []
        for order in range(order_max + 1):
            values.append(self.sum(order))
        return values

    def sum(self, order=None):
        if order is None:
            maximum = sys.maxsize
        else:
            maximum = order
        result = 0
        for xi, map in self.map.items():
            if xi > 2 * maximum:
                continue
            result += self.get(xi)
        return result

    @classmethod
    def key(cls, xi, k):
        return f"{xi}-{k}"