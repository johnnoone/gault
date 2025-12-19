from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from bson import ObjectId

from .types import AsRef, ExpressionOperator, QueryPredicate

if TYPE_CHECKING:
    from .types import Context, MongoExpression, MongoField, MongoPath, MongoQuery


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


def compile_expression(obj: Any, *, context: Context) -> MongoExpression:
    match obj:
        case ExpressionOperator():
            return obj.compile_expression(context=context)
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
            return obj
        case _:
            msg = f"compile expression is not implemented for type {type(obj)}"
            raise CompilationError(msg, target=obj)


def compile_path(obj: Any, *, context: Context) -> MongoPath:
    match obj:
        case AsRef():
            return obj.compile_expression(context=context)
        case str() if obj.startswith("$"):
            return obj
        case str() if not obj.startswith("$"):
            msg = f"Value {obj!r} looks like a field"
            raise CompilationError(msg, target=obj)
        case _:
            msg = f"compile path is not implemented for type {type(obj)}"
            raise CompilationError(msg, target=obj)


def compile_field(obj: Any, *, context: Context) -> MongoField:
    match obj:
        case AsRef():
            return obj.compile_field(context=context)
        case str() if not obj.startswith("$"):
            return obj
        case str() if obj.startswith("$"):
            msg = f"Value {obj!r} looks like a path"
            raise CompilationError(msg, target=obj)
        case _:
            msg = f"compile field is not implemented for type {type(obj)}"
            raise CompilationError(msg, target=obj)
