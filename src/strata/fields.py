from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .types import Context, ExpressionOperator, MongoValue, QueryPredicate

if TYPE_CHECKING:
    from .predicates import FieldMatcher


@ExpressionOperator.register
@QueryPredicate.register
class AsField(ABC):
    @abstractmethod
    def compile_field(self, *, context: Context) -> str:
        raise NotImplementedError

    def compile_expression(self, *, context: Context) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Var(AsField):
    value: str

    def compile_field(self, *, context: Context) -> str:
        return self.value

    def compile_expression(self, *, context: Context) -> str:
        return "$$" + self.value


@dataclass
class Field(AsField):
    value: str

    def compile_field(self, *, context: Context) -> str:
        return self.value

    def compile_expression(self, *, context: Context) -> str:
        return "$" + self.value
