from amaranth import Shape, ShapeLike, unsigned, Value
from amaranth.lib.wiring import Signature, Flow, Member
from amaranth_types import AbstractInterface, AbstractSignature

from typing import Any, Mapping, Optional

__all__ = [
    "ComponentSignal",
    "CIn",
    "COut",
    "ComponentInterface",
    "FlippedComponentInterface",
]


class ComponentSignal(Value):
    """Component Signal
    Element of `ComponentInterface`. Use `CIn` and `COut` wrappers.

    It is compatible with `Signal` for type checking and stores information for `Signature` construction.
    It should never be referenced in HDL and exist only on type level.
    Real `Signal` is created in place of `ComponentSignal` in `Component` constructor.
    """

    _flow: Flow  # Don't access directly - flips are not applied here.
    _shape: Shape

    def __init__(self, flow: Flow, shape: Optional[ShapeLike] = None):
        """
        Parameters
        ----------
        flow: Flow
            Direction of `Signal` member. `Flow.In` or `Flow.Out`.
        shape: Optional ShapeLike
            Shape of `Signal` member. `unsigned(1)` by default.
        """
        self._shape = unsigned(1) if shape is None else Shape.cast(shape)
        self._flow = flow

    def as_member(self):
        return self._flow(self._shape)

    # Value abstract methods
    def shape(self):
        return self._shape

    def _rhs_signals(self):
        # Should never be called - only used from HDL
        raise NotImplementedError

    # Signal API compatiblitly types (Signal is @final, Value is used instead)
    name: str
    decoder: Any


class CIn(ComponentSignal):
    """`ComponentSignal` with `Flow.In` direction."""

    def __init__(self, shape: Optional[ShapeLike] = None):
        super().__init__(Flow.In, shape)


class COut(ComponentSignal):
    """`ComponentSignal` with `Flow.Out` direction."""

    def __init__(self, shape: Optional[ShapeLike] = None):
        super().__init__(Flow.Out, shape)


class ComponentInterface(AbstractInterface[AbstractSignature]):
    """Component Interface
    Syntactic sugar for using typed lib.wiring `Signature`s in `Component`.

    It allows to avoid defining desired Amaranth `Signature` and separetly `AbstractInterface` of `Signals` to get
    `Component` attribute-level typing of interface.

    Interface should be constructed in `__init__` of class that inherits `ComponentInterface`, by defining
    instance attributes.
    Only allowed attributes in `ComponentInterface` are of `ComponentSignal` (see `CIn` and `COut`)
    and `ComponentInterface` (nested interface) types.

    Resulting class can be used directly as typing hint for class-level interface attribute, that will be later
    constructed  by `Component`. Use `signature` property to get amaranth `Signature` in `Component` constructor.

    Examples
    --------
    .. highlight:: python
    .. code-block:: python
        class ExampleInterface(ComponentInterface):
            def __init__(self, data_width: int):
                self.data_in = CIn(data_width)
                self.data_out = COut(data_width)
                self.valid = CIn()
                self.x = SubInterface().flipped()

        class Example(Component):
            bus: ExampleInterface
            def __init__(self):
                super().__init__({bus: In(ExampleInterface(2).signature)})
    """

    @property
    def signature(self) -> AbstractSignature:
        """Amaranth lib.wiring `Signature` constructed from defined `ComponentInterface` attributes."""
        return Signature(self._to_members_list())

    def flipped(self) -> "FlippedComponentInterface":
        """`ComponentInterface` with flipped `Flow` direction of members."""
        return FlippedComponentInterface(self)

    def _to_members_list(self, *, name_prefix: str = "") -> Mapping[str, Member]:
        res = {}
        for m_name in dir(self):
            if m_name.startswith("_") or m_name == "signature" or m_name == "flipped":
                continue

            m_val = getattr(self, m_name)
            if isinstance(m_val, ComponentSignal):
                res[m_name] = m_val.as_member()
            elif isinstance(m_val, ComponentInterface):
                res[m_name] = Flow.Out(m_val.signature)
            else:
                raise AttributeError(
                    f"Illegal attribute `{name_prefix+m_name}`. Expected `CIn`, `COut` or `ComponentInterface`"
                )
        return res


class FlippedComponentInterface(ComponentInterface):
    """
    Represents another `ComponentInterface` with flipped `Flow` directions of its members.
    Flip is applied only in resulting `signature` property.
    """

    def __init__(self, base: ComponentInterface):
        self._base = base

    def __getattr__(self, name: str):
        return getattr(self._base, name)

    @property
    def signature(self) -> AbstractSignature:
        """Amaranth lib.wiring `Signature` constructed from defined `ComponentInterface` attributes."""
        return self._base.signature.flip()

    def flipped(self) -> "FlippedComponentInterface":
        """`ComponentInterface` with flipped `Flow` direction of members."""
        return FlippedComponentInterface(self)
