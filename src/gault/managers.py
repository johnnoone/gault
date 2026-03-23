from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Any, Generic, TypeAlias
from weakref import WeakKeyDictionary, WeakSet

from pymongo import ReturnDocument
from typing_extensions import TypeVar

from .exceptions import Forbidden, NotFound, Unprocessable
from .mappers import get_mapper
from .models import Model, Page, Schema, get_collection, unwrap_model
from .pipelines import Pipeline, RawStep
from .predicates import Predicate, Raw

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from pymongo.asynchronous.database import AsyncDatabase
    from pymongo.synchronous.database import Database

    from .pipelines import Stage
    from .sorting import SortPayload
    from .types import Document, MongoQuery

    Filter: TypeAlias = Predicate | Pipeline | MongoQuery | list[Stage] | None

M = TypeVar("M", bound="Model")
S = TypeVar("S", bound="Schema")


def _normalize_filter(filter: Filter) -> Pipeline:
    match filter:
        case None:
            return Pipeline()
        case list():
            return Pipeline(steps=[RawStep(stage) for stage in filter])  # ty:ignore[invalid-argument-type]
        case Predicate():
            return Pipeline().match(filter)
        case Mapping():
            return Pipeline().match(Raw(filter))  # ty:ignore[invalid-argument-type]
        case Pipeline():
            return filter
        case _:
            msg = f"Unsupported filter type: {type(filter).__name__}"
            raise NotImplementedError(msg)


class StateTracker:
    def __init__(self) -> None:
        self._states: WeakKeyDictionary[Model, Any] = WeakKeyDictionary()

    def snapshot(self, instance: Model) -> None:
        self._states[instance] = deepcopy(instance.__dict__)

    def reset(self, instance: Model) -> None:
        instance.__dict__ = deepcopy(self._states[instance])

    def get_dirty_fields(self, instance: Model) -> set[str]:
        dirty_fields = set()
        if snapshoted := self._states.get(instance):
            state = instance.__dict__
            for key, val in snapshoted.items():
                if state[key] != val:
                    dirty_fields.add(key)
        return dirty_fields


class Persistence:
    def __init__(self) -> None:
        self._instances: WeakSet[Model] = WeakSet()

    def is_persisted(self, instance: Model) -> bool:
        return instance in self._instances

    def mark_persisted(self, instance: Model) -> None:
        self._instances.add(instance)

    def forget(self, instance: Model) -> None:
        self._instances.remove(instance)


class AsyncManager:
    def __init__(
        self,
        database: AsyncDatabase[Document],
        *,
        persistence: Persistence | None = None,
        state_tracker: StateTracker | None = None,
    ) -> None:
        self.database = database
        self._persistence = persistence
        self._state_tracker = state_tracker

    @cached_property
    def persistence(self) -> Persistence:
        persistence = self._persistence = self._persistence or Persistence()
        return persistence

    @cached_property
    def state_tracker(self) -> StateTracker:
        state_tracker = self._state_tracker = self._state_tracker or StateTracker()
        return state_tracker

    async def get(self, model: type[M], filter: Filter = None) -> M:
        if instance := await self.find(model, filter):
            return instance
        raise NotFound(model, filter)

    async def find(
        self,
        model: type[M],
        filter: Filter = None,
    ) -> M | None:
        async for instance in self.select(model, filter, take=1):
            return instance
        return None

    async def select(
        self,
        model: type[M],
        filter: Filter = None,
        *,
        skip: int | None = None,
        take: int | None = None,
    ) -> AsyncIterator[M]:
        filter = _normalize_filter(filter)

        if skip:
            filter = filter.skip(skip)
        if take:
            filter = filter.take(take)
        filter = filter.project(model).build()
        collection = get_collection(model)

        if filter and "$documents" in filter[0]:
            # {"$documents": …} stage can be performed by database only
            func = self.database.aggregate
        else:
            func = self.database.get_collection(collection).aggregate

        cursor = await func(
            pipeline=filter,
        )

        mapper = get_mapper(model)
        async for document in cursor:
            instance = mapper.map(document)
            self.persistence.mark_persisted(instance)
            self.state_tracker.snapshot(instance)
            yield instance

    async def insert(self, instance: S) -> S:
        if not isinstance(instance, Schema):
            raise Forbidden(
                unwrap_model(instance),
                reason="Only model allowed for insert",
            )
        document = get_mapper(instance).to_document(instance)
        collection = get_collection(instance)
        await self.database.get_collection(collection).insert_one(document)
        self.persistence.mark_persisted(instance)
        self.state_tracker.snapshot(instance)
        return instance

    async def insert_many(self, instances: list[S]) -> list[S]:
        if not instances:
            return []
        for instance in instances:
            if not isinstance(instance, Schema):
                raise Forbidden(
                    unwrap_model(instance),
                    reason="Only schema allowed for insert",
                )
        mapper = get_mapper(instances[0])
        documents = [mapper.to_document(inst) for inst in instances]
        collection = get_collection(instances[0])
        await self.database.get_collection(collection).insert_many(documents)
        for instance in instances:
            self.persistence.mark_persisted(instance)
            self.state_tracker.snapshot(instance)
        return instances

    async def delete_many(self, model: type[S], filter: Filter = None) -> int:
        query = _normalize_filter(filter).build()
        collection = get_collection(model)
        # Extract $match from pipeline stages to get the query filter
        mongo_filter: dict[str, Any] = {}
        for stage in query:
            if "$match" in stage:
                mongo_filter.update(stage["$match"])
        result = await self.database.get_collection(collection).delete_many(mongo_filter)
        return result.deleted_count

    async def update_many(
        self,
        model: type[S],
        *,
        update: dict[str, Any],
        filter: Filter = None,
    ) -> int:
        query = _normalize_filter(filter).build()
        collection = get_collection(model)
        mongo_filter: dict[str, Any] = {}
        for stage in query:
            if "$match" in stage:
                mongo_filter.update(stage["$match"])
        result = await self.database.get_collection(collection).update_many(
            mongo_filter, update
        )
        return result.modified_count

    async def distinct(
        self,
        model: type[M],
        *,
        field: str,
        filter: Filter = None,
    ) -> list[Any]:
        query = _normalize_filter(filter).build()
        collection = get_collection(model)
        mongo_filter: dict[str, Any] = {}
        for stage in query:
            if "$match" in stage:
                mongo_filter.update(stage["$match"])
        return await self.database.get_collection(collection).distinct(field, mongo_filter)

    async def save(
        self,
        instance: S,
        *,
        refresh: bool = False,
        atomic: bool = False,
    ) -> S:
        if not isinstance(instance, Schema):
            raise Forbidden(
                unwrap_model(instance),
                reason="Only model allowed for insert",
            )

        mapper = get_mapper(instance)
        filter = {}
        atomic = atomic and self.persistence.is_persisted(instance)
        dirty_fields = self.state_tracker.get_dirty_fields(instance)

        on_insert = {}
        on_update = {}
        for model_field, db_field, value, pk in mapper.iter_document(instance):
            if pk:
                filter[db_field] = {"$eq": value}
            elif atomic and model_field not in dirty_fields:
                on_insert[db_field] = value
            else:
                on_update[db_field] = value

        if not filter:
            raise Unprocessable(
                unwrap_model(instance),
                reason="model must declare one field as pk",
            )

        update = {}
        if on_insert:
            update["$setOnInsert"] = on_insert
        if on_update:
            update["$set"] = on_update

        collection = get_collection(instance)
        document = await self.database.get_collection(collection).find_one_and_update(
            filter=filter,
            update=update,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if refresh is True:
            persisted = mapper.map(document)
            instance.__dict__ = persisted.__dict__

        self.persistence.mark_persisted(instance)
        self.state_tracker.snapshot(instance)
        return instance

    async def refresh(self, instance: M) -> M:
        collection = get_collection(instance)
        mapper = get_mapper(instance)
        filter = mapper.to_filter(instance)

        if not filter:
            raise Unprocessable(
                unwrap_model(instance),
                reason="model must declare one field as pk",
            )

        if document := await self.database.get_collection(collection).find_one(filter):
            persisted = mapper.map(document)
            instance.__dict__ = persisted.__dict__
            self.persistence.mark_persisted(instance)
            return instance
        raise NotFound(type(instance), filter)

    async def count(self, model: type[M], filter: Filter = None) -> int:
        pipeline = _normalize_filter(filter).count("total").build()
        collection = get_collection(model)
        cursor = await self.database.get_collection(collection).aggregate(pipeline)
        async for document in cursor:
            return document["total"]  # type: ignore[no-any-return]
        return 0

    async def exists(self, model: type[M], filter: Filter = None) -> bool:
        return await self.count(model, filter) > 0

    async def delete(self, instance: S) -> None:
        if not isinstance(instance, Schema):
            raise Forbidden(
                unwrap_model(instance),
                reason="Only schema allowed for delete",
            )
        mapper = get_mapper(instance)
        filter = mapper.to_filter(instance)
        if not filter:
            raise Unprocessable(
                unwrap_model(instance),
                reason="model must declare one field as pk",
            )
        collection = get_collection(instance)
        await self.database.get_collection(collection).delete_one(filter)
        self.persistence.forget(instance)

    async def paginate(
        self,
        model: type[M],
        filter: Filter = None,
        *,
        page: int = 1,
        per_page: int = 10,
        sort_by: SortPayload | None = None,
    ) -> Page[M]:
        pipeline = _normalize_filter(filter).facet(
            Pipeline().count("total").alias("total"),
            Pipeline()
            .sort(sort_by)
            .skip((page - 1) * per_page)
            .take(per_page)
            .project(model)
            .alias("instances"),
        ).build()

        collection = get_collection(model)

        if pipeline and "$documents" in pipeline[0]:
            # {"$documents": …} stage can be performed by database only
            func = self.database.aggregate
        else:
            func = self.database.get_collection(collection).aggregate

        cursor = await func(pipeline=pipeline)

        mapper = get_mapper(model)
        document = await cursor.next()
        total = document["total"][0]["total"] if document["total"] else 0
        instances: list[M] = []
        for sub_document in document["instances"]:
            instance = mapper.map(sub_document)
            self.persistence.mark_persisted(instance)
            self.state_tracker.snapshot(instance)
            instances.append(instance)
        return Page(instances=instances, total=total, page=page, per_page=per_page)


class Manager(Generic[M, S]):
    def __init__(
        self,
        database: Database[Document],
        *,
        persistence: Persistence | None = None,
        state_tracker: StateTracker | None = None,
    ) -> None:
        self.database = database
        self._persistence = persistence
        self._state_tracker = state_tracker

    @cached_property
    def persistence(self) -> Persistence:
        persistence = self._persistence = self._persistence or Persistence()
        return persistence

    @cached_property
    def state_tracker(self) -> StateTracker:
        state_tracker = self._state_tracker = self._state_tracker or StateTracker()
        return state_tracker

    def get(self, model: type[M], filter: Filter = None) -> M:
        if instance := self.find(model, filter):
            return instance
        raise NotFound(model, filter)

    def find(
        self,
        model: type[M],
        filter: Filter = None,
    ) -> M | None:
        for instance in self.select(model, filter, take=1):
            return instance
        return None

    def select(
        self,
        model: type[M],
        filter: Filter = None,
        *,
        skip: int | None = None,
        take: int | None = None,
    ) -> Iterator[M]:
        filter = _normalize_filter(filter)

        if skip:
            filter = filter.skip(skip)
        if take:
            filter = filter.take(take)
        filter = filter.project(model).build()
        collection = get_collection(model)

        if filter and "$documents" in filter[0]:
            # {"$documents": …} stage can be performed by database only
            func = self.database.aggregate
        else:
            func = self.database.get_collection(collection).aggregate

        cursor = func(
            pipeline=filter,
        )

        mapper = get_mapper(model)
        for document in cursor:
            instance = mapper.map(document)
            self.persistence.mark_persisted(instance)
            self.state_tracker.snapshot(instance)
            yield instance

    def insert(self, instance: S) -> S:
        if not isinstance(instance, Schema):
            raise Forbidden(
                unwrap_model(instance),
                reason="Only model allowed for insert",
            )
        document = get_mapper(instance).to_document(instance)
        collection = get_collection(instance)
        self.database.get_collection(collection).insert_one(document)
        self.persistence.mark_persisted(instance)
        self.state_tracker.snapshot(instance)
        return instance

    def insert_many(self, instances: list[S]) -> list[S]:
        if not instances:
            return []
        for instance in instances:
            if not isinstance(instance, Schema):
                raise Forbidden(
                    unwrap_model(instance),
                    reason="Only schema allowed for insert",
                )
        mapper = get_mapper(instances[0])
        documents = [mapper.to_document(inst) for inst in instances]
        collection = get_collection(instances[0])
        self.database.get_collection(collection).insert_many(documents)
        for instance in instances:
            self.persistence.mark_persisted(instance)
            self.state_tracker.snapshot(instance)
        return instances

    def delete_many(self, model: type[S], filter: Filter = None) -> int:
        query = _normalize_filter(filter).build()
        collection = get_collection(model)
        mongo_filter: dict[str, Any] = {}
        for stage in query:
            if "$match" in stage:
                mongo_filter.update(stage["$match"])
        result = self.database.get_collection(collection).delete_many(mongo_filter)
        return result.deleted_count

    def update_many(
        self,
        model: type[S],
        *,
        update: dict[str, Any],
        filter: Filter = None,
    ) -> int:
        query = _normalize_filter(filter).build()
        collection = get_collection(model)
        mongo_filter: dict[str, Any] = {}
        for stage in query:
            if "$match" in stage:
                mongo_filter.update(stage["$match"])
        result = self.database.get_collection(collection).update_many(
            mongo_filter, update
        )
        return result.modified_count

    def distinct(
        self,
        model: type[M],
        *,
        field: str,
        filter: Filter = None,
    ) -> list[Any]:
        query = _normalize_filter(filter).build()
        collection = get_collection(model)
        mongo_filter: dict[str, Any] = {}
        for stage in query:
            if "$match" in stage:
                mongo_filter.update(stage["$match"])
        return self.database.get_collection(collection).distinct(field, mongo_filter)

    def save(
        self,
        instance: S,
        *,
        refresh: bool = False,
        atomic: bool = False,
    ) -> S:
        if not isinstance(instance, Schema):
            raise Forbidden(
                unwrap_model(instance),
                reason="Only model allowed for insert",
            )

        mapper = get_mapper(instance)
        filter = {}
        atomic = atomic and self.persistence.is_persisted(instance)
        dirty_fields = self.state_tracker.get_dirty_fields(instance)

        on_insert = {}
        on_update = {}
        for model_field, db_field, value, pk in mapper.iter_document(instance):
            if pk:
                filter[db_field] = {"$eq": value}
            elif atomic and model_field not in dirty_fields:
                on_insert[db_field] = value
            else:
                on_update[db_field] = value

        if not filter:
            raise Unprocessable(
                unwrap_model(instance),
                reason="model must declare one field as pk",
            )

        update = {}
        if on_insert:
            update["$setOnInsert"] = on_insert
        if on_update:
            update["$set"] = on_update

        collection = get_collection(instance)
        document = self.database.get_collection(collection).find_one_and_update(
            filter=filter,
            update=update,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if refresh is True:
            persisted = mapper.map(document)
            instance.__dict__ = persisted.__dict__

        self.persistence.mark_persisted(instance)
        self.state_tracker.snapshot(instance)
        return instance

    def refresh(self, instance: M) -> M:
        collection = get_collection(instance)
        mapper = get_mapper(instance)
        filter = mapper.to_filter(instance)

        if not filter:
            raise Unprocessable(
                unwrap_model(instance),
                reason="model must declare one field as pk",
            )

        if document := self.database.get_collection(collection).find_one(filter):
            persisted = mapper.map(document)
            instance.__dict__ = persisted.__dict__
            self.persistence.mark_persisted(instance)
            return instance
        raise NotFound(type(instance), filter)

    def count(self, model: type[M], filter: Filter = None) -> int:
        pipeline = _normalize_filter(filter).count("total").build()
        collection = get_collection(model)
        cursor = self.database.get_collection(collection).aggregate(pipeline)
        for document in cursor:
            return document["total"]  # type: ignore[no-any-return]
        return 0

    def exists(self, model: type[M], filter: Filter = None) -> bool:
        return self.count(model, filter) > 0

    def delete(self, instance: S) -> None:
        if not isinstance(instance, Schema):
            raise Forbidden(
                unwrap_model(instance),
                reason="Only schema allowed for delete",
            )
        mapper = get_mapper(instance)
        filter = mapper.to_filter(instance)
        if not filter:
            raise Unprocessable(
                unwrap_model(instance),
                reason="model must declare one field as pk",
            )
        collection = get_collection(instance)
        self.database.get_collection(collection).delete_one(filter)
        self.persistence.forget(instance)

    def paginate(
        self,
        model: type[M],
        filter: Filter = None,
        *,
        page: int = 1,
        per_page: int = 10,
        sort_by: SortPayload | None = None,
    ) -> Page[M]:
        pipeline = _normalize_filter(filter).facet(
            Pipeline().count("total").alias("total"),
            Pipeline()
            .sort(sort_by)
            .skip((page - 1) * per_page)
            .take(per_page)
            .project(model)
            .alias("instances"),
        ).build()

        collection = get_collection(model)

        if pipeline and "$documents" in pipeline[0]:
            # {"$documents": …} stage can be performed by database only
            func = self.database.aggregate
        else:
            func = self.database.get_collection(collection).aggregate

        cursor = func(pipeline=pipeline)

        mapper = get_mapper(model)
        document = next(cursor)
        total = document["total"][0]["total"] if document["total"] else 0
        instances: list[M] = []
        for sub_document in document["instances"]:
            instance = mapper.map(sub_document)
            self.persistence.mark_persisted(instance)
            self.state_tracker.snapshot(instance)
            instances.append(instance)
        return Page(instances=instances, total=total, page=page, per_page=per_page)
