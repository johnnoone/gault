from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self
from typing import Literal as TypingLiteral

from annotated_types import Ge, Predicate
from bson import Binary as BSONBinary
from bson import Decimal128 as BSONDecimal
from bson import ObjectId
from bson import Regex as BSONRegex

if TYPE_CHECKING:
    from .models import Model, Schema


type Document = dict[str, Any]
RawPath = Annotated[str, Predicate(lambda x: x.startswith("$"))]
RawField = Annotated[str, Predicate(lambda x: not x.startswith("$"))]

PositiveInteger = Annotated[int, Ge(0)]


class AttributeBase:
    __slots__ = ("db_alias", "name", "owner")

    def __init__(
        self,
        owner: type[Schema | Model],
        name: str,
        db_alias: str | None = None,
    ) -> None:
        self.owner = owner
        self.name = name
        self.db_alias = db_alias or name


## mongo types

type MongoField = str
type MongoExpression[T: Any] = Any
type MongoQuery = dict[MongoExpression, MongoExpression]
type Context = Any
type MongoType = str | int
type MongoVar = str
type MongoValue = Scalar | Array[MongoValue] | Object[String, MongoValue]


type Scalar = String | Regex | Binary | Number | Null | Boolean | ObjectId | Date


type Regex = str | BSONRegex

type String = str
"""An expression that resolves to a string"""


type Number = int | float | BSONDecimal | Decimal
"""An expression that resolves to an integer or long"""

type Boolean = bool
"""An expression that resolves to a boolean value"""

type Null = None
"""An expression that resolves to null"""

type Binary = bytes | BSONBinary
"""An expression that resolves to a binary string"""

type Array[T: Any] = list[Any]
"""An expression that resolves to an array"""

type Object[K: str, V: Any] = dict[K, V]
"""An expression that resolves to an object"""

type Date = datetime
"""An expression that resolves to a date"""

type DateUnit = TypingLiteral[
    "year",
    "quarter",
    "week",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "millisecond",
]

type DayWeek = TypingLiteral[
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

type Timezone = Any
type Direction = TypingLiteral[1, -1] | dict[str, Any]


class QueryPredicate(ABC):
    @abstractmethod
    def compile_query(self, context: Context) -> MongoQuery:
        raise NotImplementedError


class ExpressionOperator(ABC):
    @abstractmethod
    def compile_expression(self, context: Context) -> MongoExpression:
        raise NotImplementedError


@dataclass
class Aliased[T]:
    ref: str
    value: T


class AsAlias:
    def alias(self, ref: str) -> Aliased[Self]:
        return Aliased(ref, self)


class DBAlias(ABC):
    db_name: str


@ExpressionOperator.register
@QueryPredicate.register
class AsRef(ABC):
    @abstractmethod
    def compile_field(self, *, context: Context) -> str:
        raise NotImplementedError

    @abstractmethod
    def compile_expression(self, *, context: Context) -> str:
        raise NotImplementedError


class FieldSortInterface:
    name: str

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
        prefixed = self.name + "." + name
        return replace(self, name=prefixed)
