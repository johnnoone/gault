from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Generic,
    Self,
    TypeAlias,
    TypeVar,
    cast,
)
from typing import Literal as TypingLiteral

from bson import ObjectId

T = TypeVar("T")
K_co = TypeVar("K_co", covariant=True)
V_co = TypeVar("V_co", covariant=True)
T_co = TypeVar("T_co", covariant=True)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime
    from decimal import Decimal

    from annotated_types import Ge, Predicate
    from bson import Binary as BSONBinary
    from bson import Decimal128 as BSONDecimal
    from bson import Regex as BSONRegex

    from .inout import MongoExpression
    from .models import Model

    Document: TypeAlias = Mapping[str, "MongoValue"]
    """A mongo document"""

    PositiveInteger: TypeAlias = Annotated[int, Ge(0)]

    MongoField: TypeAlias = str
    MongoPath: TypeAlias = str

    Input: TypeAlias = T | "Expr" | "DollarString"
    """An expression that resolves to given type"""

    MongoQuery: TypeAlias = Mapping[MongoField | str, Input]
    Context: TypeAlias = Any

    Regex: TypeAlias = str | BSONRegex

    String: TypeAlias = str
    """An expression that resolves to a string"""

    Number: TypeAlias = int | float | BSONDecimal | Decimal
    """An expression that resolves to an integer or long"""

    Boolean: TypeAlias = bool
    """An expression that resolves to a boolean value"""

    Null: TypeAlias = None | "RefLike" | "Expr"
    """An expression that resolves to null"""

    Binary: TypeAlias = bytes | BSONBinary
    """An expression that resolves to a binary string"""

    Array: TypeAlias = list[T] | "RefLike" | "Expr"
    """An expression that resolves to an array"""

    Object: TypeAlias = Mapping[K_co, V_co]
    """An expression that resolves to an object"""

    Date: TypeAlias = datetime
    """An expression that resolves to a date"""

    Scalar: TypeAlias = (
        String | Regex | Binary | Number | Null | Boolean | ObjectId | Date
    )
    MongoValue: TypeAlias = (
        Scalar | Array["MongoValue"] | Object["String", "MongoValue"]
    )

    DateUnit: TypeAlias = TypingLiteral[
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

    DayWeek: TypeAlias = TypingLiteral[
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    Timezone: TypeAlias = Any
    Direction: TypeAlias = TypingLiteral[1, -1] | Mapping[str, Any]

    RefLike: TypeAlias = "AsRef" | str

    _StrType = TypeVar("_StrType", bound=str)

    DollarString = Annotated[_StrType, Predicate(lambda x: str.startswith(x, "$"))]
    Expr: TypeAlias = Mapping[DollarString, Any]


class AttributeBase:
    __slots__ = ("db_alias", "name", "owner")

    def __init__(
        self,
        owner: type[Model],
        name: str,
        db_alias: str | None = None,
    ) -> None:
        self.owner = owner
        self.name = name
        self.db_alias = db_alias or name


class QueryPredicate(ABC):
    @abstractmethod
    def compile_query(self, *, context: Context) -> MongoQuery:
        raise NotImplementedError


class ExpressionOperator(ABC):
    @abstractmethod
    def compile_expression(self, *, context: Context) -> MongoExpression:
        raise NotImplementedError


@dataclass
class Aliased(Generic[T_co]):
    ref: str
    value: T_co


class AsAlias:
    def alias(self, ref: str) -> Aliased[Self]:
        return Aliased(ref, self)


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

    def asc(self) -> tuple[Self, Direction]:
        # generate sort token
        return (self, 1)

    def desc(self) -> tuple[Self, Direction]:
        # generate sort token
        return (self, -1)

    def by_score(self, name: str) -> tuple[Self, Direction]:
        # generate sort token
        return (self, {"$meta": name})


class TempFieldInterface:
    @classmethod
    def tmp(cls) -> Self:
        # instantiate field with a random name
        name = f"__{ObjectId().__str__()}"
        return cls(name)  # type: ignore[call-arg]


class SubfieldInterface:
    name: str

    def field(self, name: str) -> Self:
        # access a sub field
        prefixed = self.name + "." + name
        return replace(  # type: ignore[no-any-return]
            cast("Any", self),
            name=prefixed,
        )
