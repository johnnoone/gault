from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .types import AsRef, AttributeBase, Context


class Operator(ABC):
    @abstractmethod
    def compile(self, *, context: Context) -> Any: ...

    def __and__(self, other: Operator) -> And:
        return And(operators=[self, other])

    def __or__(self, other: Operator) -> Or:
        return Or(operators=[self, other])

    def __invert__(self) -> Not:
        return Not(self)


@dataclass
class And(Operator):
    operators: list[Operator]

    def __and__(self, other: Operator) -> And:
        if isinstance(other, And):
            operators = other.operators
        else:
            operators = [other]
        return And(operators=self.operators + operators)

    def compile(self, *, context: Context) -> Any:
        return {
            "$and": [operator.compile(context=context) for operator in self.operators],
        }


@dataclass
class Or(Operator):
    operators: list[Operator]

    def __or__(self, other: Operator) -> Or:
        if isinstance(other, Or):
            operators = other.operators
        else:
            operators = [other]
        return Or(operators=self.operators + operators)

    def compile(self, *, context: Context) -> Any:
        return {
            "$or": [operator.compile(context=context) for operator in self.operators],
        }


@dataclass
class Not(Operator):
    operator: Operator

    def __invert__(self) -> Operator:
        return self.operator

    def compile(self, *, context: Context) -> Any:
        return {
            "$not": self.operator.compile(context=context),
        }


@dataclass
class Eq(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$eq": val}}


@dataclass
class Ne(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$ne": val}}


@dataclass
class Lt(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$lt": val}}


@dataclass
class Lte(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$lte": val}}


@dataclass
class Gt(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$gt": val}}


@dataclass
class Gte(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$gte": val}}


@dataclass
class In(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$in": val}}


@dataclass
class Nin(Operator):
    lhs: Any
    rhs: Any

    def compile(self, *, context: Context) -> Any:
        key = prepare_lhs(self.lhs, context=context)
        val = prepare_rhs(self.rhs, context=context)
        return {key: {"$nin": val}}


def prepare_lhs(obj: Any, *, context: Context) -> str:
    if isinstance(obj, AttributeBase):
        return obj.db_alias
    if isinstance(obj, AsRef):
        return obj.compile_field(context=context)
    if isinstance(obj, str):
        return obj

    raise NotImplementedError


def prepare_rhs(obj: Any, *, context: Context) -> Any:
    if isinstance(obj, AttributeBase):
        return "$" + obj.db_alias
    if isinstance(obj, AsRef):
        return obj.compile_expression(context=context)
    return obj
