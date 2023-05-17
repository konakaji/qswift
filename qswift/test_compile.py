from unittest import TestCase
from qswift.compiler import *
from qswift.initializer import XBasisInitializer
from qwrapper.operator import PauliObservable


class TestQSwiftCircuitEncoder(TestCase):
    def test_encode(self):
        channel = SwiftChannel(2.2)
        channel.add_time_operators([-1, -1, 2])
        channel.add_swift_operator(-1, 0)
        channel.set_measurement_operator(0)
        s_encoder = QSwiftStringEncoder()
        code = s_encoder.encode(channel)
        self.assertEquals("2.2 T-1 T-1 T2 S-1:0 M0", code)
        paulis = {-1: PauliObservable("XXXIIIII"), 2: PauliObservable("YYYIIIII")}
        observables = {0: PauliObservable("XZZZIIIII")}
        encoder = QSwiftCircuitExecutor(paulis, observables, XBasisInitializer(), 0.1, nshot=10)
        encoder.compute(code)


class TestQSwiftImplementableEncoder(TestCase):
    def test_encode(self):
        channels = SwiftChannel(2)
        channels.add_time_operators([0, 0])
        channels.add_swift_operator(1, 0)
        channels.add_time_operators([0, 0])
        channels.add_swift_operator(1, 1)
        channels.set_measurement_operator(0)
        s_encoder = QSwiftStringEncoder()
        self.assertEquals("2 T0 T0 S1:0 T0 T0 S1:1 M0", s_encoder.encode(channels))


class TestCompiler(TestCase):
    def test_to_strings(self):
        compiler = Compiler(operators=[PauliObservable("XX"), PauliObservable("YY"), PauliObservable("ZZ")],
                            observables=[PauliObservable("ZY"), PauliObservable("XY")], initializer=XBasisInitializer(),
                            tau=2)
        channels = SwiftChannel(0.1)
        channels.add_time_operators([2, 1])
        channels.add_swift_operator(0, 0)
        channels.set_measurement_operator(0)
        strs = compiler.to_string(channels)
        self.assertEquals("0.1 T2 T1 S0:0 M0", strs)
