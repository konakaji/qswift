from unittest import TestCase
from qswiftencoder.encoder import *
from qwrapper.operator import PauliObservable
from qwrapper.circuit import init_circuit


class TestQSwiftCircuitEncoder(TestCase):
    def test_encode(self):
        operators = []
        for _ in range(10):
            operators.append(TimeOperator("-1"))
        operators.append(SwiftOperator("-1", 0))
        operators.append(MeasurementOperator(0))
        s_encoder = QSwiftStringEncoder()
        code = s_encoder.encode(2.2, operators)
        self.assertEquals("2.2 T-1 T-1 T-1 T-1 T-1 T-1 T-1 T-1 T-1 T-1 S-1:0 M0", code)
        paulis = {-1: PauliObservable("XXXIIIII")}
        observables = {0: PauliObservable("XZZZIIIII")}
        encoder = QSwiftCircuitExecutor(paulis, observables, 0.1)

        qc = init_circuit(9, "qulacs")
        encoder.compute(qc, code)


class TestQSwiftImplementableEncoder(TestCase):
    def test_encode(self):
        channels = SwiftChannels(2)
        channels.add_time_operators([0, 0])
        channels.add_l_operator(1)
        channels.add_time_operators([0, 0])
        channels.add_l_operator(2)
        channels.set_measurement_operator(0)
        encoder = QSwiftImplementableEncoder()
        rs = encoder.encode(channels)

        s_encoder = QSwiftStringEncoder()
        self.assertEquals("2 T0 T0 S1:0 T0 T0 S2:0 M0", s_encoder.encode(2, rs[0]))
        self.assertEquals("2 T0 T0 S1:0 T0 T0 S2:1 M0", s_encoder.encode(2, rs[1]))
        self.assertEquals("2 T0 T0 S1:1 T0 T0 S2:0 M0", s_encoder.encode(2, rs[2]))
        self.assertEquals("2 T0 T0 S1:1 T0 T0 S2:1 M0", s_encoder.encode(2, rs[3]))


class TestCompiler(TestCase):
    def test_to_strings(self):
        compiler = Compiler(operators=["XX", "YY", "ZZ"], observables=["ZY", "XY"], tau=2)
        channels = SwiftChannels(0.1)
        channels.add_time_operators([2, 1])
        channels.add_l_operator(0)
        channels.set_measurement_operator(0)
        strs = compiler.to_strings(channels)
        self.assertEquals("0.1 T2 T1 S0:0 M0", strs[0])
        self.assertEquals("0.1 T2 T1 S0:1 M0", strs[1])
