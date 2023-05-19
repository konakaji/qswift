import logging
import random
from unittest import TestCase
from qwrapper.hamiltonian import Hamiltonian, to_matrix_hamiltonian
from qwrapper.obs import PauliObservable
from benchmark.molecule import MolecularHamiltonian

from qswift.exact import ExactComputation
from qswift.initializer import XBasisInitializer
from qswift.qswift import QSwift

if __name__ == '__main__':
    t = 1
    logging.getLogger("qswift.executor.QSwiftExecutor").setLevel(logging.DEBUG)
    logging.getLogger("qswift.qswift.QSwift").setLevel(logging.INFO)
    obs = Hamiltonian([1], [PauliObservable("ZIIIIIII")], 8)
    hamiltonian = MolecularHamiltonian(8, "6-31g", "hydrogen")
    initializer = XBasisInitializer()

    exact = ExactComputation(to_matrix_hamiltonian(obs),
                             to_matrix_hamiltonian(hamiltonian), t, initializer)
    ex = exact.compute()

    N = 200
    qswift = QSwift(obs, initializer, t=t, N=N, K=2, nshot=0, n_p=10000, tool="qulacs")
    result = qswift.evaluate(hamiltonian)
    print(ex, result.sum(0), result.sum(1), result.sum(2))
