from unittest import TestCase
from qwrapper.operator import PauliTimeEvolution, PauliObservable
from qwrapper.hamiltonian import HeisenbergModel
from qwrapper.circuit import init_circuit
from qswift.initializer import ZBasisInitializer
from qswift.sequence import Sequence
from qswift.compiler import DefaultOperatorPool


class TestSequence(TestCase):
    def test_evaluate(self):
        qc = init_circuit(4, "qulacs")
        paulis = [PauliObservable("XYII"), PauliObservable("IIXY")]
        ev0 = PauliTimeEvolution(paulis[0], 0.1)
        ev1 = PauliTimeEvolution(paulis[1], 0.1)
        ev2 = PauliTimeEvolution(paulis[1], 0.2)
        # ev4 = PauliTimeEvolution(paulis[1], 0.2)
        ev4 = PauliTimeEvolution(paulis[1], 0.4)

        ev0.add_circuit(qc)
        ev1.add_circuit(qc)
        ev2.add_circuit(qc)
        ev4.add_circuit(qc)

        obs = HeisenbergModel(4)
        initializer = ZBasisInitializer()

        operator_pool = DefaultOperatorPool(paulis)

        seq = Sequence(obs, initializer, operator_pool, taus=[0.1, 0.2, 0.4])
        self.assertAlmostEquals(obs.exact_value(qc), seq.evaluate([0, 1, 2, 4]))
