from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import MISSING, dataclass, field, fields, replace
from functools import cached_property, singledispatchmethod
from typing import (
    TYPE_CHECKING,
    Any,
    NamedTuple,
    Self,
    TypedDict,
    TypeVar,
    Unpack,
    cast,
    dataclass_transform,
    overload,
)
from weakref import WeakKeyDictionary, WeakValueDictionary

from pymongo import ReturnDocument

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from pymongo.asynchronous.database import AsyncDatabase

T = TypeVar("T", bound=Any)
M = TypeVar("M", bound="Model")


MAPPERS: dict[type[Model], Mapper] = WeakKeyDictionary()
MODELS: dict[str, type[Model]] = WeakValueDictionary()
COLLECTIONS: dict[type[Model], str] = WeakKeyDictionary()


def get_collection(model: Model | type[Model]) -> str:
    model = unwrap_model(model)
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


class FieldMetadata(TypedDict, total=False):
    pk: bool
    db_alias: str


def configure(
    **metadata: Unpack[FieldMetadata],
) -> Any:
    metadata = drop_missing(metadata)
    return field(metadata=metadata)


def drop_missing[T: Mapping](mapping: T) -> T:
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


type Filter = Operator | Pipeline | dict | list | None


@dataclass
class NotFound(LookupError):
    model: type[Model]
    filter: Filter

    def __post_init__(self) -> None:
        msg = f"Instance of {self.model.__name__} not found"
        super().__init__(msg)


@dataclass
class Unprocessable(ValueError):
    model: type[Model]
    reason: str

    def __post_init__(self) -> None:
        msg = f"Unprocessable {self.model.__name__} ; {self.reason}"
        super().__init__(msg)


class AsyncManager:
    def __init__(self, database: AsyncDatabase) -> None:
        self.database = database

    async def get[M: "Model"](self, model: type[M], filter: Filter = None) -> M:
        if instance := await self.find(model, filter):
            return instance
        raise NotFound(model, filter)

    async def find[M: "Model"](self, model: type[M], filter: Filter = None) -> M | None:
        async for instance in self.select(model, filter, take=1):
            return instance
        return None

    async def select[M: "Model"](
        self,
        model: type[M],
        filter: Filter = None,
        *,
        skip: int | None = None,
        take: int | None = None,
    ) -> AsyncIterator[M]:
        match filter:
            case None:
                filter = Pipeline()
            case list():
                filter = Pipeline(stages=filter)
            case dict() | Operator():
                filter = Pipeline().match(filter)

        if skip:
            filter = filter.skip(take)
        if take:
            filter = filter.take(take)
        filter = filter.project(model).build()
        collection = get_collection(model)
        cursor = await self.database.get_collection(collection).aggregate(
            pipeline=filter,
        )

        mapper = get_mapper(model)
        async for document in cursor:
            instance = mapper.map(document)
            yield instance

    async def insert(self, instance: M) -> M:
        document = {}
        for field in fields(instance):
            name = field.name
            alias = cast("FieldMetadata", field.metadata).get("db_alias")
            document[alias or name] = getattr(instance, name)
        collection = get_collection(instance)
        await self.database.get_collection(collection).insert_one(document)
        return instance

    async def save(self, instance: M) -> M:
        document = {}
        for field in fields(instance):
            name = field.name
            alias = cast("FieldMetadata", field.metadata).get("db_alias")
            document[alias or name] = getattr(instance, name)

        mapper = get_mapper(instance)
        filter = {}
        on_update = {}
        for model_field, db_field, pk in mapper.field_mapping:
            if pk:
                filter[db_field] = {"$eq": getattr(instance, model_field)}
            else:
                on_update[db_field] = getattr(instance, model_field)

        if not filter:
            raise Unprocessable(
                unwrap_model(instance), reason="model must declare one field as pk"
            )

        update = {}
        if on_update:
            update["$set"] = on_update

        collection = get_collection(instance)
        document = await self.database.get_collection(collection).find_one_and_update(
            filter=filter,
            update=update,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        return mapper.map(document)


def get_mapper(model: M | type[M]) -> Mapper[M]:
    model = unwrap_model(model)
    if mapper := MAPPERS.get(model):
        return mapper
    mapper = MAPPERS[model] = Mapper(model)
    return mapper


def unwrap_model(model: M | type[M]) -> type[M]:
    if isinstance(model, Model):
        model = type(model)
    return model


class Mapper[M: "Model"]:
    def __init__(self, model: type[M]) -> None:
        self.model = model

    @cached_property
    def field_mapping(self) -> list[Corres]:
        result = []
        for field in fields(self.model):
            model_field = field.name
            metadata = cast("FieldMetadata", field.metadata)
            db_field = metadata.get("db_alias")
            pk = metadata.get("pk") or False
            result.append(Corres(model_field, db_field or model_field, pk=pk))
        return result

    @cached_property
    def db_fields(self) -> set[str]:
        return {corres.db_field for corres in self.field_mapping}

    def map(self, document: Document) -> M:
        attrs = {}
        for corres in self.field_mapping:
            attrs[corres.model_field] = document.get(corres.db_field, MISSING)
            attrs = drop_missing(attrs)
        return self.model(**attrs)


class Corres(NamedTuple):
    model_field: str
    db_field: str
    pk: bool


type Stage = dict[str, Any]


@dataclass
class Pipeline:
    stages: list[Stage] = field(default_factory=list)

    @singledispatchmethod
    def match(self, query: dict) -> Self:
        stage = {"$match": query}
        return replace(self, stages=[*self.stages, stage])

    @match.register
    def _(self, query: Operator) -> Self:
        stage = {"$match": query.compile()}
        return replace(self, stages=[*self.stages, stage])

    def skip(self, value: int) -> Self:
        stage = {"$skip": value}
        return replace(self, stages=[*self.stages, stage])

    def take(self, value: int) -> Self:
        stage = {"$limit": value}
        return replace(self, stages=[*self.stages, stage])

    def project(self, model: type[Model]) -> list[Stage]:
        projection = dict.fromkeys(get_mapper(model).db_fields, True)

        if projection:
            stage = {"$project": {"_id": False} | projection}
            return replace(self, stages=[*self.stages, stage])
        return self

    def build(self) -> list[Stage]:
        return list(self.stages)


async def to_list[T: Any](iterator: AsyncIterator[T]) -> list[T]:
    return [instance async for instance in iterator]


type Document = dict[str, Any]
