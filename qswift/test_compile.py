from unittest import TestCase
from qswift.compiler import *
from qswift.initializer import XBasisInitializer
from qwrapper.operator import PauliObservable


class TestQSwiftCircuitEncoder(TestCase):
    def test_encode(self):
        channel = SwiftChannel(2.2)
        channel.add_time_operators([-1, -1, 2])
        channel.add_l_operator(-1)
        channel.set_measurement_operator(0)
        s_encoder = QSwiftStringEncoder()
        codes = s_encoder.encode(channel)
        self.assertEquals("2.2 T-1 T-1 T2 S-1:0 M0", codes[0])
        self.assertEquals("2.2 T-1 T-1 T2 S-1:1 M0", codes[1])
        paulis = {-1: PauliObservable("XXXIIIII"), 2: PauliObservable("YYYIIIII")}
        observables = {0: PauliObservable("XZZZIIIII")}
        encoder = QSwiftCircuitExecutor(operator_pool=DefaultOperatorPool(paulis),
                                        observables=observables, initializer=XBasisInitializer(),
                                        tau=0.1, nshot=10)
        for code in codes:
            encoder.compute(code)


class TestQSwiftImplementableEncoder(TestCase):
    def test_encode(self):
        channels = SwiftChannel(2)
        channels.add_time_operators([0, 0])
        channels.add_l_operator(1)
        channels.add_time_operators([0, 0])
        channels.add_l_operator(1)
        channels.set_measurement_operator(0)
        s_encoder = QSwiftStringEncoder()
        code = s_encoder.encode(channels)
        self.assertEquals("2 T0 T0 S1:0 T0 T0 S1:0 M0", code[0])
        self.assertEquals("2 T0 T0 S1:0 T0 T0 S1:1 M0", code[1])
        self.assertEquals("2 T0 T0 S1:1 T0 T0 S1:0 M0", code[2])
        self.assertEquals("2 T0 T0 S1:1 T0 T0 S1:1 M0", code[3])


class TestCompiler(TestCase):
    def test_to_strings(self):
        compiler = Compiler(
            operator_pool=DefaultOperatorPool([PauliObservable("XX"), PauliObservable("YY"), PauliObservable("ZZ")]),
            observables=[PauliObservable("ZY"), PauliObservable("XY")], initializer=XBasisInitializer(),
            tau=2)
        channels = SwiftChannel(0.1)
        channels.add_time_operators([2, 1])
        channels.add_swift_operator(0, 0)
        channels.set_measurement_operator(0)
        strs = compiler.to_string(channels)[0]
        self.assertEquals("0.1 T2 T1 S0:0 M0", strs)
