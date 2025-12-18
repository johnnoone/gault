from __future__ import annotations

from dataclasses import MISSING, dataclass, field, fields
from typing import Any, Literal, Self, TypedDict, Unpack, dataclass_transform, overload
from weakref import WeakKeyDictionary, WeakValueDictionary

from pymongo import ASCENDING, DESCENDING

from .operators import Eq, Gt, Gte, In, Lt, Lte, Ne, Nin, Operator
from .predicates import FieldMatcherInterface
from .types import (
    AsRef,
    AttributeBase,
    Context,
    FieldSortInterface,
    FieldUtilInterface,
    MongoExpression,
)
from .utils import drop_missing

SCHEMAS: dict[str, type[Schema]] = WeakValueDictionary()
COLLECTIONS: dict[type[Schema | Model], str] = WeakKeyDictionary()


def unwrap_model(
    model: Schema | Model | type[Schema | Model],
) -> type[Schema | Model]:
    if isinstance(model, Schema | Model):
        model = type(model)
    return model


def get_collection(model: type[Schema | Model] | Schema | Model) -> str:
    model = unwrap_model(model)
    return COLLECTIONS[model]


def get_schema(collection: str) -> type[Schema]:
    return SCHEMAS[collection]


@dataclass_transform(kw_only_default=True)
class Model:
    def __init_subclass__(cls, collection: str | None = None) -> None:
        dataclass(cls, init=True, repr=True, kw_only=True)
        for dataclass_field in fields(cls):
            field = Attribute(name=dataclass_field.name, **dataclass_field.metadata)
            setattr(cls, dataclass_field.name, field)

        cls.__hash__ = object.__hash__

        COLLECTIONS[cls] = collection


@dataclass_transform(kw_only_default=True)
class Schema(Model, collection=None):
    def __init_subclass__(cls, collection: str) -> None:
        if collection is None:
            msg = "collection is required"
            raise ValueError(msg)

        super().__init_subclass__(collection=collection)
        SCHEMAS[collection] = cls


class AttributeSpec[T: Any](
    AttributeBase,
    AsRef,
    FieldMatcherInterface,
    FieldSortInterface,
    FieldUtilInterface,
):
    def compile_field(self, *, context: Context) -> str:
        return self.db_alias

    def compile_expression(self, *, context: Context) -> str:
        return "$" + self.db_alias

    def get_db_alias(self) -> str:
        return self.db_alias

    def __hash__(self) -> None:
        return hash((self.owner, self.name, self.db_alias))

    def eq(self, other: T | MongoExpression) -> Operator:
        return Eq(self, other)

    def ne(self, other: T | MongoExpression) -> Operator:
        return Ne(self, other)

    def lt(self, other: T | MongoExpression) -> Operator:
        return Lt(self, other)

    def lte(self, other: T | MongoExpression) -> Operator:
        return Lte(self, other)

    def gt(self, other: T | MongoExpression) -> Operator:
        return Gt(self, other)

    def gte(self, other: T | MongoExpression) -> Operator:
        return Gte(self, other)

    def in_(self, other: T | MongoExpression) -> Operator:
        return In(self, other)

    def nin(self, other: T | MongoExpression) -> Operator:
        return Nin(self, other)

    def asc(self) -> tuple[Self, Literal[-1]]:
        return (self, ASCENDING)

    def desc(self) -> tuple[Self, Literal[-1]]:
        return (self, DESCENDING)

    def by_score(self, name: str) -> tuple[Self, dict]:
        return (self, {"$meta": name})

    __eq__ = eq
    __ne__ = ne
    __lt__ = lt
    __le__ = lte
    __gt__ = gt
    __ge__ = gte


class Attribute[T: Any]:
    def __init__(
        self,
        *,
        name: str | None = None,
        pk: bool = bool,
        db_alias: str | None = None,
    ) -> None:
        self.name: str | None = name
        self.pk = pk
        self.db_alias = db_alias

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> AttributeSpec[T]: ...

    @overload
    def __get__(self, instance: object, owner: type) -> T: ...

    def __get__(self, instance: object | None, owner: type) -> T | AttributeSpec[T]:
        if instance is None:
            return AttributeSpec(owner, self.name, db_alias=self.db_alias)
        return instance.__dict__[self.name]

    def __set__(self, instance: object, value: T) -> None:
        instance.__dict__[self.name] = value


class AttributeMetadata(TypedDict, total=False):
    pk: bool
    db_alias: str


def configure(
    *,
    default: Any = MISSING,
    **metadata: Unpack[AttributeMetadata],
) -> Any:
    metadata = drop_missing(metadata)
    return field(default=default, metadata=metadata)
