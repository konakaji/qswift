import random
import sys

import numpy as np
from bitarray.util import int2ba
from qwrapper.sampler import ImportantSampler, FasterImportantSampler
from qswift.measurement import Measurement
from qswift.compiler import MultiIndexSampler, SwiftChannel


class QSwiftSampler:
    def __init__(self, k, xi, n_vec, sampler: ImportantSampler, N) -> None:
        self.k = k
        self.xi = xi
        self.n_vec = n_vec
        self.N = N
        self.sampler = sampler
        self.mi_sampler = MultiIndexSampler(self.sampler)
        assert self.xi == np.sum(n_vec)

    def sample(self, measurements: [Measurement]) -> [SwiftChannel]:
        results = []
        if self.xi == 0:
            for m in measurements:
                swift_channel = SwiftChannel(1)
                swift_channel.add_time_operators(self.sampler.sample_indices(self.N - self.k))
                m.assign(swift_channel)
                results.append(swift_channel)
            return results
        for s_list in self._s_list():
            for b_vecs in self._b_list():
                for m in measurements:
                    swift_channel = SwiftChannel(self._sign(s_list) * 1)
                    for b_vec, s, n in zip(b_vecs, s_list, self.n_vec):
                        swift_channel.add_multi_swift_operators(self.mi_sampler.sample(s, n), b_vec)
                    swift_channel.add_time_operators(self.sampler.sample_indices(self.N - self.k))
                    swift_channel.shuffle(random.randint(0, sys.maxsize))
                    m.assign(swift_channel)
                    results.append(swift_channel)
        return results

    def _sign(self, s):
        count = 0
        for v in s:
            if v == 1:
                count += v
        if count % 2 == 0:
            return 1
        else:
            return -1

    def _s_list(self):
        for val in range(pow(2, self.k)):
            array = int2ba(val, self.k)
            yield array.tolist()

    def _b_list(self):
        for val in range(pow(2, self.xi)):
            array = int2ba(val, self.xi)
            yield self._to_blist(array)

    def _to_blist(self, bit_array):
        results = []
        current = 0
        for j in range(self.k):
            results.append(bit_array[current: current + self.n_vec[j]].tolist())
            current = current + self.n_vec[j]
        return results
