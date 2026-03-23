from __future__ import annotations

import pytest
from pymongo.asynchronous.database import AsyncDatabase

from gault.exceptions import Forbidden, NotFound, Unprocessable
from gault.managers import AsyncManager, Persistence, _normalize_filter
from gault.models import Attribute, Model, Schema, configure
from gault.pipelines import Pipeline
from gault.utils import to_list


class Person(Schema, collection="coverage-collection"):
    id: Attribute[int] = configure(pk=True)
    name: Attribute[str]
    age: Attribute[int]


class NoPkModel(Schema, collection="coverage-collection"):
    name: Attribute[str]
    age: Attribute[int]


class NotASchema(Model, collection="coverage-notschema"):
    name: Attribute[str]


@pytest.fixture(name="people")
async def get_people(database: AsyncDatabase, persistence: Persistence):
    await database.get_collection("coverage-collection").insert_many(
        [
            {"id": 1, "name": "alice", "age": 30},
            {"id": 2, "name": "bob", "age": 25},
            {"id": 3, "name": "charlie", "age": 35},
        ]
    )
    people = [
        Person(id=1, name="alice", age=30),
        Person(id=2, name="bob", age=25),
        Person(id=3, name="charlie", age=35),
    ]
    for person in people:
        persistence.mark_persisted(person)
    return people


class TestNormalizeFilter:
    def test_list_of_raw_stages(self):
        """Line 39: _normalize_filter with list of raw stages."""
        stages = [{"$match": {"name": "alice"}}]
        result = _normalize_filter(stages)
        assert isinstance(result, Pipeline)

    def test_dict_filter(self):
        """Line 43: _normalize_filter with dict filter."""
        result = _normalize_filter({"name": "alice"})
        assert isinstance(result, Pipeline)

    def test_unsupported_type(self):
        """Lines 46-47: _normalize_filter with unsupported type."""
        with pytest.raises(NotImplementedError):
            _normalize_filter(42)


@pytest.mark.usefixtures("people")
async def test_select_with_skip(manager: AsyncManager):
    """Line 131: select with skip parameter."""
    iterator = manager.select(Person, skip=1)
    results = await to_list(iterator)
    assert len(results) == 2


async def test_save_model_with_no_pk(manager: AsyncManager):
    """Line 196: save model with no pk raises Unprocessable."""
    instance = NoPkModel(name="alice", age=30)
    with pytest.raises(Unprocessable):
        await manager.save(instance)


async def test_refresh_model_with_no_pk(manager: AsyncManager):
    """Line 228: refresh model with no pk raises Unprocessable."""
    instance = NoPkModel(name="alice", age=30)
    with pytest.raises(Unprocessable):
        await manager.refresh(instance)


@pytest.mark.usefixtures("people")
async def test_refresh_non_existent_document(manager: AsyncManager):
    """Line 238: refresh non-existent document raises NotFound."""
    instance = Person(id=9999, name="ghost", age=0)
    with pytest.raises(NotFound):
        await manager.refresh(instance)


@pytest.mark.usefixtures("people")
async def test_select_with_list_filter(manager: AsyncManager):
    """Line 39 via select: select with list of raw stages."""
    stages = [{"$match": {"name": "alice"}}]
    iterator = manager.select(Person, filter=stages)
    results = await to_list(iterator)
    assert len(results) == 1
    assert results[0].name == "alice"


@pytest.mark.usefixtures("people")
async def test_find_with_dict_filter(manager: AsyncManager):
    """Line 43 via find: find with dict filter."""
    result = await manager.find(Person, filter={"name": "alice"})
    assert result is not None
    assert result.name == "alice"


@pytest.mark.usefixtures("people")
async def test_count(manager: AsyncManager):
    total = await manager.count(Person)
    assert total == 3


@pytest.mark.usefixtures("people")
async def test_count_with_filter(manager: AsyncManager):
    total = await manager.count(Person, filter=Person.age >= 30)
    assert total == 2


async def test_count_empty(manager: AsyncManager):
    total = await manager.count(Person)
    assert total == 0


@pytest.mark.usefixtures("people")
async def test_exists(manager: AsyncManager):
    assert await manager.exists(Person, filter=Person.id == 1) is True
    assert await manager.exists(Person, filter=Person.id == 9999) is False


async def test_delete(manager: AsyncManager):
    person = Person(id=100, name="to-delete", age=20)
    await manager.insert(person)
    assert await manager.exists(Person, filter=Person.id == 100) is True

    await manager.delete(person)
    assert await manager.exists(Person, filter=Person.id == 100) is False


async def test_delete_non_schema_raises_forbidden(manager: AsyncManager):
    instance = NotASchema(name="alice")
    with pytest.raises(Forbidden):
        await manager.delete(instance)


async def test_delete_no_pk_raises_unprocessable(manager: AsyncManager):
    instance = NoPkModel(name="alice", age=30)
    with pytest.raises(Unprocessable):
        await manager.delete(instance)


async def test_paginate_with_documents_pipeline(manager: AsyncManager):
    """Line 263: paginate with $documents pipeline (uses database.aggregate)."""
    pipeline = Pipeline.documents(
        [
            {"id": 10, "name": "doc1", "age": 20},
            {"id": 11, "name": "doc2", "age": 21},
            {"id": 12, "name": "doc3", "age": 22},
        ]
    )
    page = await manager.paginate(Person, filter=pipeline)
    assert page.total == 3
    assert page.page == 1
    assert page.per_page == 10
    assert len(page.instances) == 3
