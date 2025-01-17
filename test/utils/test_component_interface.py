from unittest import TestCase

from amaranth import Signal
from amaranth.lib.wiring import Component, Flow, In
from transactron.utils.amaranth_ext.component_interface import CIn, COut, ComponentInterface, ComponentSignal

class SubSubInterface(ComponentInterface):
    def __init__(self):
        self.i = CIn()

class SubInterface(ComponentInterface):
    def __init__(self):
        self.i = CIn()
        self.f = SubSubInterface().flipped()

class TestInterface(ComponentInterface):
    def __init__(self):
        self.i = CIn(2)
        self.o = COut(2)
        self.s = SubInterface()
        self.f = SubInterface().flipped()
        self.uf = SubInterface().flipped().flipped()

class TestComponentInterface(TestCase):
    def test_a(self):
        class TestComponent(Component):
            iface: TestInterface

            def __init__(self):
                super().__init__({"iface": In(TestInterface().signature)})
        
        t = TestComponent()

        assert isinstance(t.iface.i, Signal)
        assert isinstance(t.iface.s.i, Signal)
        assert isinstance(t.iface.f.i, Signal)
        
        ci = TestInterface()
        sig = ci.signature

        assert sig.members["s"].signature.members["i"].flow is Flow.In
        assert sig.members["f"].signature.members["i"].flow is Flow.Out
        assert sig.members["uf"].signature.members["i"].flow is Flow.In
        
        assert ci.s.i._flow is Flow.In
        #assert ci.f.i._flow is Flow.Out
        
        #assert sig.s.i.f.i.flow is Flow.Out
        #assert sig.s.f.f.i.flow is Flow.In
        #assert sig.s.uf.f.i.flow is Flow.Out

        assert isinstance(ci.i, ComponentSignal)
        assert isinstance(ci.f.i, ComponentSignal)
        assert isinstance(ci.uf.f.i, ComponentSignal)
