from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Literal, Self

from bson import ObjectId

from .types import Context, ExpressionOperator, QueryPredicate


@ExpressionOperator.register
@QueryPredicate.register
class AsField(ABC):
    @abstractmethod
    def compile_field(self, *, context: Context) -> str:
        raise NotImplementedError

    def compile_expression(self, *, context: Context) -> str:
        raise NotImplementedError


class FieldSortInterface:
    def asc(self) -> tuple[Self, Literal[-1]]:
        # generate sort token
        return (self, 1)

    def desc(self) -> tuple[Self, Literal[-1]]:
        # generate sort token
        return (self, -1)

    def by_score(self, name: str) -> tuple[Self, dict]:
        # generate sort token
        return (self, {"$meta": name})


class FieldUtilInterface:
    value: str

    @classmethod
    def tmp(cls) -> Self:
        # instantiate field with a random name
        name = f"__{ObjectId().__str__()}"
        return cls(name)

    def field(self, name: str) -> Self:
        # access a sub field
        value = self.value + "." + name
        return replace(self, value=value)
