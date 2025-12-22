from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Self,
    TypeVar,
    cast,
)

from bson import ObjectId

T = TypeVar("T")
K_co = TypeVar("K_co", covariant=True)
V_co = TypeVar("V_co", covariant=True)
T_co = TypeVar("T_co", covariant=True)

if TYPE_CHECKING:
    from .models import Model
    from .types import Context, Direction, MongoExpression, MongoQuery


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
