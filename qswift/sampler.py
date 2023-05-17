import random
import sys

import numpy as np
from bitarray.util import int2ba
from qwrapper.sampler import FasterImportantSampler

from qswift.compiler import MultiIndexSampler, SwiftChannel


class QSwiftSampler:
    def __init__(self, k, xi, n_vec, hs, obs_hs, N) -> None:
        self.k = k
        self.xi = xi
        self.n_vec = n_vec
        self.N = N
        self.sampler = FasterImportantSampler(hs)
        self.obs_sampler = FasterImportantSampler(obs_hs)
        self.mi_sampler = MultiIndexSampler(self.sampler)
        assert self.xi == np.sum(n_vec)

    def sample(self, n_p) -> [SwiftChannel]:
        results = []
        if self.xi == 0:
            for _ in range(n_p):
                swift_channel = SwiftChannel(1 / n_p)
                swift_channel.add_time_operators(self.sampler.sample_indices(self.N - self.k))
                results.append(swift_channel)
            self._set_measurements(results)
            return results
        for _ in range(n_p):
            for s_list in self._s_list():
                for b_vecs in self._b_list():
                    swift_channel = SwiftChannel(self._sign(s_list) * 1 / n_p)
                    for b_vec, s, n in zip(b_vecs, s_list, self.n_vec):
                        swift_channel.add_multi_swift_operators(self.mi_sampler.sample(s, n), b_vec)
                    swift_channel.add_time_operators(self.sampler.sample_indices(self.N - self.k))
                    swift_channel.shuffle(random.randint(0, sys.maxsize))
                    results.append(swift_channel)
        self._set_measurements(results)
        return results

    def _set_measurements(self, swift_channels: [SwiftChannel]):
        for swift_channel, index in zip(swift_channels, self.obs_sampler.sample_indices(len(swift_channels))):
            swift_channel.set_measurement_operator(index)

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