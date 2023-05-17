from abc import ABC, abstractmethod
from qswift.compiler import SwiftChannel
import math


class Measurement:
    def __init__(self, coeff, index):
        self.coeff = coeff
        self.index = index

    def assign(self, channel: SwiftChannel):
        channel.coeff = channel.coeff * self.coeff
        channel.set_measurement_operator(self.index)


class MeasureGenerator(ABC):
    @abstractmethod
    def generate(self, n_sample):
        pass


class NaiveGenerator(MeasureGenerator):
    def __init__(self, hs):
        self.hs = hs

    def generate(self, n_sample) -> [Measurement]:
        measurements = []
        count = math.ceil(n_sample / len(self.hs))
        for _ in range(count):
            for j, h in enumerate(self.hs):
                measurements.append(Measurement(h / count, j))
        return measurements
