# from dataclasses import dataclass, replace
# from enum import Enum
# from typing import Any, Self, TypeAlias, TypeVar
# from amaranth import *
# from transactron.utils import *
# from .method import MethodSignature
#
#
# T = TypeVar("T")
#
#
# MemberDescription: TypeAlias = "MethodSignature | MethodsSignature"
#
#
# class Direction(Enum):
#     Import = "import"
#     Export = "export"
#
#     def __call__(self, description: MemberDescription) -> "Member":
#         return Member(self, description)
#
#     def flip(self) -> Self:
#         match self:
#             case Direction.Import:
#                 return Direction.Export
#             case Direction.Export:
#                 return Direction.Import
#
#
# @dataclass
# class ArraySignature:
#     description: MemberDescription
#
#
# @dataclass
# class Member:
#     flow: Direction
#     description: MemberDescription
#
#     def flip(self):
#         return replace(self, flow=self.flow.flip())
#
#
# @dataclass
# class MethodsSignature:
#     members: Mapping[str, Member]
#
#     def flip(self):
#         return replace(self, members={k: m.flip() for k, m in self.members.items()})
#
#     def create(self, *, path: tuple[str | int, ...], src_loc_at=0):
#         attrs: dict[str, Any] = {}
#         return attrs
#
#
# class WithMethods:
#     methods_signature: MethodsSignature
