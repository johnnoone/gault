from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, field, fields
from typing import Any, TypeVar, dataclass_transform, overload
from weakref import WeakKeyDictionary, WeakValueDictionary

T = TypeVar("T", bound=Any)


MODELS: dict[str, type[Model]] = WeakValueDictionary()
COLLECTIONS: dict[type[Model], str] = WeakKeyDictionary()


def get_collection(model: Model | type[Model]) -> str:
    if isinstance(model, Model):
        model = type(model)
    return COLLECTIONS[model]


def get_model(collection: str) -> type[Model]:
    return MODELS[collection]


@dataclass_transform()
class Model:
    def __init_subclass__(cls, collection: str) -> None:
        dataclass(cls, init=True, repr=True, unsafe_hash=True)
        for dataclass_field in fields(cls):
            field = Field(name=dataclass_field.name, **dataclass_field.metadata)
            setattr(cls, dataclass_field.name, field)
        MODELS[collection] = cls
        COLLECTIONS[cls] = collection


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


def configure(
    *,
    pk: bool = MISSING,
    db_alias: str = MISSING,
) -> Any:
    metadata = drop_missing({"pk": pk, "db_alias": db_alias})
    return field(metadata=metadata)


def drop_missing(mapping: dict[str, Any]) -> dict[str, Any]:
    return {key: val for key, val in mapping.items() if val is not MISSING}


class Attribute[T: Any]:
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

    def __hash__(self) -> None:
        return hash((self.owner, self.name, self.db_alias))

    def eq(self, other: Any) -> Operator:
        return Eq(self, other)

    def ne(self, other: Any) -> Operator:
        return Ne(self, other)

    def lt(self, other: Any) -> Operator:
        return Lt(self, other)

    def lte(self, other: Any) -> Operator:
        return Lte(self, other)

    def gt(self, other: Any) -> Operator:
        return Gt(self, other)

    def gte(self, other: Any) -> Operator:
        return Gte(self, other)

    def in_(self, other: Any) -> Operator:
        return In(self, other)

    def nin(self, other: Any) -> Operator:
        return Nin(self, other)

    __eq__ = eq
    __ne__ = ne
    __lt__ = lt
    __le__ = lte
    __gt__ = gt
    __ge__ = gte


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
    if isinstance(obj, Attribute):
        return obj.db_alias
    if isinstance(obj, str):
        return obj

    raise NotImplementedError


def prepare_rhs(obj: Any) -> Any:
    if isinstance(obj, Path):
        return "$" + obj.value
    if isinstance(obj, Attribute):
        return "$" + obj.db_alias
    return obj


@dataclass
class Path:
    value: str
