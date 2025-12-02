from __future__ import annotations

from dataclasses import MISSING, dataclass, field, fields
from typing import Any, Literal, Self, TypedDict, Unpack, dataclass_transform, overload
from weakref import WeakKeyDictionary, WeakValueDictionary

from pymongo import ASCENDING, DESCENDING

from .operators import Eq, Gt, Gte, In, Lt, Lte, Ne, Nin, Operator
from .types import AttributeBase, Path
from .utils import drop_missing

MODELS: dict[str, type[Model]] = WeakValueDictionary()
COLLECTIONS: dict[type[Model | Projection], str] = WeakKeyDictionary()


def unwrap_model(
    model: Model | Projection | type[Model | Projection],
) -> type[Model | Projection]:
    if isinstance(model, Model | Projection):
        model = type(model)
    return model


def get_collection(model: type[Model | Projection] | Model | Projection) -> str:
    model = unwrap_model(model)
    return COLLECTIONS[model]


def get_model(collection: str) -> type[Model]:
    return MODELS[collection]


@dataclass_transform(kw_only_default=True)
class Model:
    def __init_subclass__(cls, collection: str) -> None:
        dataclass(cls, init=True, repr=True, kw_only=True)
        for dataclass_field in fields(cls):
            field = Field(name=dataclass_field.name, **dataclass_field.metadata)
            setattr(cls, dataclass_field.name, field)

        cls.__hash__ = object.__hash__

        MODELS[collection] = cls
        COLLECTIONS[cls] = collection


@dataclass_transform(kw_only_default=True)
class Projection:
    def __init_subclass__(cls, collection: str) -> None:
        dataclass(cls, init=True, repr=True, kw_only=True)
        for dataclass_field in fields(cls):
            field = Field(name=dataclass_field.name, **dataclass_field.metadata)
            setattr(cls, dataclass_field.name, field)

        cls.__hash__ = object.__hash__

        COLLECTIONS[cls] = collection


class Attribute[T: Any](AttributeBase):
    def __hash__(self) -> None:
        return hash((self.owner, self.name, self.db_alias))

    def eq(self, other: T | Path | Attribute) -> Operator:
        return Eq(self, other)

    def ne(self, other: T | Path | Attribute) -> Operator:
        return Ne(self, other)

    def lt(self, other: T | Path | Attribute) -> Operator:
        return Lt(self, other)

    def lte(self, other: T | Path | Attribute) -> Operator:
        return Lte(self, other)

    def gt(self, other: T | Path | Attribute) -> Operator:
        return Gt(self, other)

    def gte(self, other: T | Path | Attribute) -> Operator:
        return Gte(self, other)

    def in_(self, other: T | Path | Attribute) -> Operator:
        return In(self, other)

    def nin(self, other: T | Path | Attribute) -> Operator:
        return Nin(self, other)

    def asc(self) -> tuple[Self, Literal[-1]]:
        return (self, ASCENDING)

    def desc(self) -> tuple[Self, Literal[-1]]:
        return (self, DESCENDING)

    def by_score(self, name: str) -> tuple[Self, Literal[-1]]:
        return (self, {"$meta": name})

    __eq__ = eq
    __ne__ = ne
    __lt__ = lt
    __le__ = lte
    __gt__ = gt
    __ge__ = gte


class Field[T: Any]:
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
    def __get__(self, instance: None, owner: type) -> Attribute[T]: ...

    @overload
    def __get__(self, instance: object, owner: type) -> T: ...

    def __get__(self, instance: object | None, owner: type) -> T | Attribute[T]:
        if instance is None:
            return Attribute(owner, self.name, db_alias=self.db_alias)
        return instance.__dict__[self.name]

    def __set__(self, instance: object, value: T) -> None:
        instance.__dict__[self.name] = value


class FieldMetadata(TypedDict, total=False):
    pk: bool
    db_alias: str


def configure(
    *,
    default: Any = MISSING,
    **metadata: Unpack[FieldMetadata],
) -> Any:
    metadata = drop_missing(metadata)
    return field(default=default, metadata=metadata)
