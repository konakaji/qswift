from unittest import TestCase
from qswiftencoder.encoder import *
from qwrapper.operator import PauliObservable
from qwrapper.circuit import init_circuit


class TestQSwiftCircuitEncoder(TestCase):
    def test_encode(self):
        operators = []
        for _ in range(10):
            operators.append(TimeOperator("h"))
        operators.append(SwiftOperator("h", 0))
        s_encoder = QSwiftStringEncoder()
        code = s_encoder.encode(2.2, operators)
        self.assertEquals("2.2 Th Th Th Th Th Th Th Th Th Th Sh:0", code)

        paulis = {"h": PauliObservable("XXXIIIII")}
        encoder = QSwiftCircuitEncoder(0, [1, 2, 3, 4, 5, 6, 7, 8], paulis, 0.1)

        qc = init_circuit(9, "qulacs")
        sign, qc = encoder.encode(qc, code)

        obs = PauliObservable("XZZZIIIII")
        self.assertEquals(0, obs.exact_value(qc))


class TestQSwiftImplementableEncoder(TestCase):
    def test_encode(self):
        operators = []
        for _ in range(2):
            operators.append(TimeOperator(0))
        operators.append(LOperator(1))
        for _ in range(2):
            operators.append(TimeOperator(0))
        operators.append(LOperator(2))
        encoder = QSwiftImplementableEncoder()
        rs = encoder.encode(operators)

        s_encoder = QSwiftStringEncoder()
        self.assertEquals("2 T0 T0 S1:0 T0 T0 S2:0", s_encoder.encode(2, rs[0]))
        self.assertEquals("2 T0 T0 S1:0 T0 T0 S2:1", s_encoder.encode(2, rs[1]))
        self.assertEquals("2 T0 T0 S1:1 T0 T0 S2:0", s_encoder.encode(2, rs[2]))
        self.assertEquals("2 T0 T0 S1:1 T0 T0 S2:1", s_encoder.encode(2, rs[3]))


class TestCompiler(TestCase):
    def test_to_strings(self):
        compiler = Compiler(0, [1, 2], {0: "XX", 1: "YY", 2: "ZZ"}, 2)
        channels = SwiftChannels(0.1)
        channels.add_time_operators([2, 1])
        channels.add_l_operator(0)
        strs = compiler.to_strings(channels)
        self.assertEquals("0.1 T2 T1 S0:0", strs[0])
        self.assertEquals("0.1 T2 T1 S0:1", strs[1])
