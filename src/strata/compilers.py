from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from bson import ObjectId

from .fields import AsField
from .types import (
    Context,
    ExpressionOperator,
    MongoExpression,
    MongoField,
    MongoQuery,
    QueryPredicate,
)


def compile_field(value: Any, *, context: Context) -> MongoField:
    match value:
        case AsField():
            return value.compile_field(context=context)
        case str() if not value.startswith("$"):
            return value
        case str() if value.startswith("$"):
            msg = f"Value {value!r} looks like a path"
            raise CompilationError(msg, target=value)
        case _:
            msg = f"compile field is not implemented for type {type(value)}"
            raise CompilationError(msg, target=value)


def compile_query(value: Any, *, context: Context) -> MongoQuery:
    match value:
        case QueryPredicate():
            return value.compile_query(context=context)
        case str() | int() | float():
            return value
        case dict():
            return value
        case _:
            msg = f"compile query is not implemented for type {type(value)}"
            raise CompilationError(msg, target=value)


@dataclass
class CompilationError(Exception):
    message: str
    target: Any | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)


def compile_expression(value: Any, *, context: Context) -> MongoExpression:
    match value:
        case ExpressionOperator():
            return value.compile_expression(context=context)
        case (
            str()
            | int()
            | float()
            | bool()
            | None
            | dict()
            | list()
            | ObjectId()
            | datetime()
        ):
            return value
        case _:
            msg = f"compile expression is not implemented for type {type(value)}"
            raise CompilationError(msg, target=value)
