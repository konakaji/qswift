import math, numpy as np
from qwrapper.obs import PauliObservable
from qwrapper.hamiltonian import Hamiltonian


def binom(N, k):
    return math.factorial(N) / (math.factorial(N - k) * math.factorial(k))


def all_combinations(total, n_elements, min_value):
    results = []
    for k in range(n_elements):
        result = []
        for n in range(min_value, total + 1):
            result.append(n)
        results.append(result)
    rs = []
    for vec in np.array(np.meshgrid(*results)).T.reshape(-1, n_elements):
        if np.sum(vec) != total:
            continue
        rs.append(vec)
    return rs


def zero_state(dim):
    result = np.diag(np.zeros(dim))
    result[0][0] = 1
    return result


def make_positive(hamiltonian: Hamiltonian):
    hs = []
    paulis = []
    for h, p in zip(hamiltonian.hs, hamiltonian.paulis):
        hs.append(abs(h))
        if h < 0:
            paulis.append(PauliObservable(p.p_string, -p.sign))
        else:
            paulis.append(p)
    return Hamiltonian(hs, paulis, hamiltonian.nqubit)
