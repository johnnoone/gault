from __future__ import annotations

import pytest
from pymongo.synchronous.database import Database

from gault.exceptions import Forbidden, NotFound, Unprocessable
from gault.managers import Manager, Persistence
from gault.models import Attribute, Model, Schema, configure
from gault.pipelines import Pipeline


class Person(Schema, collection="coverage-collection"):
    id: Attribute[int] = configure(pk=True)
    name: Attribute[str]
    age: Attribute[int]


class NoPkModel(Schema, collection="coverage-collection-nopk"):
    name: Attribute[str]
    age: Attribute[int]


class NotASchema(Model, collection="coverage-collection-notschema"):
    name: Attribute[str]


@pytest.fixture(name="people")
def get_people(database: Database, persistence: Persistence):
    database.get_collection("coverage-collection").insert_many(
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


@pytest.mark.usefixtures("people")
def test_select_with_skip(manager: Manager):
    """Line 328: select with skip parameter."""
    results = list(manager.select(Person, skip=1))
    assert len(results) == 2


@pytest.mark.usefixtures("people")
def test_select_with_documents_filter(manager: Manager):
    """Line 336: select with $documents filter (uses database.aggregate)."""
    pipeline = Pipeline.documents(
        [
            {"id": 10, "name": "doc1", "age": 20},
            {"id": 11, "name": "doc2", "age": 21},
        ]
    )
    results = list(manager.select(Person, filter=pipeline))
    assert len(results) == 2
    assert results[0].name == "doc1"
    assert results[1].name == "doc2"


def test_insert_non_schema_raises_forbidden(manager: Manager):
    """Line 353: insert non-Schema raises Forbidden."""
    instance = NotASchema(name="alice")
    with pytest.raises(Forbidden):
        manager.insert(instance)


def test_save_non_schema_raises_forbidden(manager: Manager):
    """Line 372: save non-Schema raises Forbidden."""
    instance = NotASchema(name="alice")
    with pytest.raises(Forbidden):
        manager.save(instance)


def test_save_model_with_no_pk(manager: Manager):
    """Line 393: save model with no pk raises Unprocessable."""
    instance = NoPkModel(name="alice", age=30)
    with pytest.raises(Unprocessable):
        manager.save(instance)


def test_refresh_model_with_no_pk(manager: Manager):
    """Line 425: refresh model with no pk raises Unprocessable."""
    instance = NoPkModel(name="alice", age=30)
    with pytest.raises(Unprocessable):
        manager.refresh(instance)


@pytest.mark.usefixtures("people")
def test_refresh_non_existent_document(manager: Manager):
    """Line 435: refresh non-existent document raises NotFound."""
    instance = Person(id=9999, name="ghost", age=0)
    with pytest.raises(NotFound):
        manager.refresh(instance)


def test_paginate_with_documents_pipeline(manager: Manager):
    """Line 460: paginate with $documents pipeline."""
    pipeline = Pipeline.documents(
        [
            {"id": 10, "name": "doc1", "age": 20},
            {"id": 11, "name": "doc2", "age": 21},
            {"id": 12, "name": "doc3", "age": 22},
        ]
    )
    page = manager.paginate(Person, filter=pipeline)
    assert page.total == 3
    assert page.page == 1
    assert page.per_page == 10
    assert len(page.instances) == 3
