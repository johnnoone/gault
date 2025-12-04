from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .types import AttributeBase, Path


class Operator(ABC):
    @abstractmethod
    def compile(self) -> Any: ...

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

    def compile(self) -> Any:
        return {
            "$and": [operator.compile() for operator in self.operators],
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

    def compile(self) -> Any:
        return {
            "$or": [operator.compile() for operator in self.operators],
        }


@dataclass
class Not(Operator):
    operator: Operator

    def __invert__(self) -> Operator:
        return self.operator

    def compile(self) -> Any:
        return {
            "$not": self.operator.compile(),
        }


@dataclass
class Eq(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$eq": val}}


@dataclass
class Ne(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$ne": val}}


@dataclass
class Lt(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$lt": val}}


@dataclass
class Lte(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$lte": val}}


@dataclass
class Gt(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$gt": val}}


@dataclass
class Gte(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$gte": val}}


@dataclass
class In(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$in": val}}


@dataclass
class Nin(Operator):
    lhs: Any
    rhs: Any

    def compile(self) -> Any:
        key = prepare_lhs(self.lhs)
        val = prepare_rhs(self.rhs)
        return {key: {"$nin": val}}


def prepare_lhs(obj: Any) -> str:
    if isinstance(obj, Path):
        return obj.value
    if isinstance(obj, AttributeBase):
        return obj.db_alias
    if isinstance(obj, str):
        return obj

    raise NotImplementedError


def prepare_rhs(obj: Any) -> Any:
    if isinstance(obj, Path):
        return "$" + obj.value
    if isinstance(obj, AttributeBase):
        return "$" + obj.db_alias
    return obj
