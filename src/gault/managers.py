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
    """Convert any supported filter type into a Pipeline."""
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
    """Tracks document state via deep-copy snapshots for dirty field detection."""

    def __init__(self) -> None:
        self._states: WeakKeyDictionary[Model, Any] = WeakKeyDictionary()

    def snapshot(self, instance: Model) -> None:
        """Save a deep copy of the instance's current state."""
        self._states[instance] = deepcopy(instance.__dict__)

    def reset(self, instance: Model) -> None:
        """Restore the instance to its last snapshotted state."""
        instance.__dict__ = deepcopy(self._states[instance])

    def get_dirty_fields(self, instance: Model) -> set[str]:
        """Return the set of field names that changed since the last snapshot."""
        dirty_fields = set()
        if snapshoted := self._states.get(instance):
            state = instance.__dict__
            for key, val in snapshoted.items():
                if state[key] != val:
                    dirty_fields.add(key)
        return dirty_fields


class Persistence:
    """Tracks which model instances have been persisted to the database."""

    def __init__(self) -> None:
        self._instances: WeakSet[Model] = WeakSet()

    def is_persisted(self, instance: Model) -> bool:
        """Return True if the instance has been saved or loaded from the database."""
        return instance in self._instances

    def mark_persisted(self, instance: Model) -> None:
        """Mark the instance as persisted."""
        self._instances.add(instance)

    def forget(self, instance: Model) -> None:
        """Remove the instance from the persisted set."""
        self._instances.remove(instance)


class AsyncManager:
    """Asynchronous manager for MongoDB CRUD operations.

    Wraps a PyMongo ``AsyncDatabase`` and provides type-safe document
    operations with automatic persistence tracking and state snapshots.
    """

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
        """Find a single document or raise ``NotFound``.

        Like :meth:`find`, but raises instead of returning ``None``.
        """
        if instance := await self.find(model, filter):
            return instance
        raise NotFound(model, filter)

    async def find(
        self,
        model: type[M],
        filter: Filter = None,
    ) -> M | None:
        """Find a single document matching the filter, or ``None``."""
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
        """Iterate over documents matching the filter.

        Supports pagination via ``skip`` and ``take``. Each yielded
        instance is automatically marked as persisted and snapshotted.
        """
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
        """Insert a single document. Only accepts Schema instances.

        Raises ``Forbidden`` if the instance is not a Schema.
        """
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
        """Insert multiple documents in a single round trip.

        All instances must be Schema instances of the same collection.
        Raises ``Forbidden`` if any instance is not a Schema.
        """
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
        """Delete all documents matching the filter. Returns the deleted count."""
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
        """Update all documents matching the filter. Returns the modified count.

        The ``update`` parameter accepts raw MongoDB update operators
        (e.g. ``{"$set": {"field": value}}``).
        """
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
        """Return a list of distinct values for the given field."""
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
        """Upsert a document using ``find_one_and_update``.

        When ``atomic=True`` and the instance is already persisted,
        only dirty fields are sent as ``$set``; unchanged fields use
        ``$setOnInsert`` (applied only on insert, not update).

        When ``refresh=True``, the instance is updated in-place with
        the document returned from the database.

        Raises ``Forbidden`` if the instance is not a Schema, or
        ``Unprocessable`` if no primary key field is defined.
        """
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
        """Reload the instance from the database.

        Replaces all fields with the latest values. Raises ``NotFound``
        if the document no longer exists, or ``Unprocessable`` if no
        primary key is defined.
        """
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
        """Count documents matching the filter."""
        pipeline = _normalize_filter(filter).count("total").build()
        collection = get_collection(model)
        cursor = await self.database.get_collection(collection).aggregate(pipeline)
        async for document in cursor:
            return document["total"]  # type: ignore[no-any-return]
        return 0

    async def exists(self, model: type[M], filter: Filter = None) -> bool:
        """Return True if at least one document matches the filter."""
        return await self.count(model, filter) > 0

    async def delete(self, instance: S) -> None:
        """Delete a single document by its primary key.

        Raises ``Forbidden`` if the instance is not a Schema, or
        ``Unprocessable`` if no primary key is defined.
        """
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
        """Return a paginated result set.

        Uses a ``$facet`` pipeline to fetch both the total count and
        the page of results in a single query.
        """
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
    """Synchronous manager for MongoDB CRUD operations.

    Wraps a PyMongo ``Database`` and provides type-safe document
    operations with automatic persistence tracking and state snapshots.
    """

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
        """Find a single document or raise ``NotFound``."""
        if instance := self.find(model, filter):
            return instance
        raise NotFound(model, filter)

    def find(
        self,
        model: type[M],
        filter: Filter = None,
    ) -> M | None:
        """Find a single document matching the filter, or ``None``."""
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
        """Iterate over documents matching the filter.

        Supports pagination via ``skip`` and ``take``.
        """
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
        """Insert a single document. Only accepts Schema instances."""
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
        """Insert multiple documents in a single round trip."""
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
        """Delete all documents matching the filter. Returns the deleted count."""
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
        """Update all documents matching the filter. Returns the modified count."""
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
        """Return a list of distinct values for the given field."""
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
        """Upsert a document using ``find_one_and_update``.

        When ``atomic=True``, only dirty fields are sent as ``$set``.
        When ``refresh=True``, the instance is updated from the database.
        """
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
        """Reload the instance from the database."""
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
        """Count documents matching the filter."""
        pipeline = _normalize_filter(filter).count("total").build()
        collection = get_collection(model)
        cursor = self.database.get_collection(collection).aggregate(pipeline)
        for document in cursor:
            return document["total"]  # type: ignore[no-any-return]
        return 0

    def exists(self, model: type[M], filter: Filter = None) -> bool:
        """Return True if at least one document matches the filter."""
        return self.count(model, filter) > 0

    def delete(self, instance: S) -> None:
        """Delete a single document by its primary key."""
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
        """Return a paginated result set using a ``$facet`` pipeline."""
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
