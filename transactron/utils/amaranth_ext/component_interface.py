from amaranth import Shape, ShapeLike, Signal, ValueLike, unsigned, Value
from amaranth.lib.wiring import FlippedSignature, Signature, Flow, Member
from amaranth_types import AbstractInterface, AbstractSignature

from copy import copy
from typing import Optional, Self

class ComponentSignal(Value):
    _flow: Flow # flow donsn't repect flips!!!
    _shape: Shape
    
    def __init__(self, flow: Flow, shape: Optional[ShapeLike] = None):
        self._shape = unsigned(1) if shape is None else Shape.cast(shape)
        self._flow = flow
    
    @property
    def member(self):
        return self._flow(self._shape)

    # Value abstract methods
    def shape(self):
        return self._shape

    def _rhs_signals(self):
        # This method should never be called
        # IOSignal is going to be substituted by a Component constructor or be used only as a type
        raise NotImplementedError

class CIn(ComponentSignal):
    def __init__(self, shape: Optional[ShapeLike] = None):
        super().__init__(Flow.In, shape)
class COut(ComponentSignal):
    def __init__(self, shape: Optional[ShapeLike] = None):
        super().__init__(Flow.Out, shape)

# is AbstractSignature needed?
# oh, we return signature -> this doesn't need to be compatiblie
# but we can make members.
# or even flippedsignature
# make flippedcomponentinterface?

class FlippedComponentInterface(AbstractInterface[AbstractSignature]):
    def __init__(self, _base: "ComponentInterface"):
        self._base = _base

    def __getattribute__(self, name: str, /):
        return self.base.__getattribute__(name)

    def signature(self):
        return Signature(Signature(self._base._to_members_list()).flip().members)

class ComponentInterface(AbstractInterface[AbstractSignature]):
    _is_flipped: bool
    
    @property
    def signature(self) -> Signature:
        signature = Signature(self._to_members_list())

        if self._get_flipped():
            # somehow better? or use in to membres list??
            return Signature(signature.flip().members)
        else:
            return signature 

    #def flipped(self) -> Self:
    #    # make new from members list?
    #    flipped = copy(self)
    #    flipped._is_flipped = not self._get_flipped()
    #    return flipped

    def flipped(self) -> FlippedComponentInterface:
        return FlippedComponentInterface(self)
    
    # or return SignatureMembers???
    def _to_members_list(self, *, name_prefix: str = "") -> dict[str, Member]:
        res = {}
        for m_name in dir(self):
            if m_name.startswith("_") or m_name == "signature" or m_name == "flipped":
                continue

            m_val = getattr(self, m_name)
            if isinstance(m_val, ComponentSignal):
                res[m_name] = m_val.member
            elif isinstance(m_val, ComponentInterface):                
                m_val_flow = Flow.In if m_val._get_flipped() else Flow.Out
                res[m_name] = m_val_flow(Signature(m_val._to_members_list(name_prefix=name_prefix+m_name+".")))
            else:
                raise AttributeError(
                        f"Illegal attribute `{name_prefix+m_name}`. "
                        "Expected CIn, COut or ComponentInterface")
            
        return res
                
    def _get_flipped(self) -> bool:
        try:
            return self._is_flipped
        except AttributeError:
            self._is_flipped = False
            return self._is_flipped

