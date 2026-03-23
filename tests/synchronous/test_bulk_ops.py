from __future__ import annotations

import pytest
from pymongo.synchronous.database import Database

from gault.exceptions import Forbidden
from gault.managers import Manager, Persistence
from gault.models import Attribute, Model, Schema, configure


class Item(Schema, collection="bulk-ops-collection"):
    id: Attribute[int] = configure(pk=True)
    name: Attribute[str]
    category: Attribute[str]
    price: Attribute[int]


class NotASchema(Model):
    name: Attribute[str]


@pytest.fixture(name="items")
def get_items(database: Database, persistence: Persistence):
    database.get_collection("bulk-ops-collection").insert_many(
        [
            {"id": 1, "name": "apple", "category": "fruit", "price": 1},
            {"id": 2, "name": "banana", "category": "fruit", "price": 2},
            {"id": 3, "name": "carrot", "category": "vegetable", "price": 3},
            {"id": 4, "name": "donut", "category": "pastry", "price": 5},
            {"id": 5, "name": "eclair", "category": "pastry", "price": 4},
        ]
    )


# --- insert_many ---


def test_insert_many(manager: Manager):
    items = [
        Item(id=10, name="fig", category="fruit", price=6),
        Item(id=11, name="grape", category="fruit", price=7),
        Item(id=12, name="ham", category="meat", price=10),
    ]
    result = manager.insert_many(items)
    assert result == items
    assert manager.count(Item) == 3


def test_insert_many_marks_persisted(manager: Manager):
    items = [
        Item(id=20, name="ice cream", category="dessert", price=5),
        Item(id=21, name="jam", category="spread", price=3),
    ]
    manager.insert_many(items)
    for item in items:
        assert manager.persistence.is_persisted(item)


def test_insert_many_empty(manager: Manager):
    result = manager.insert_many([])
    assert result == []


def test_insert_many_non_schema_raises_forbidden(manager: Manager):
    with pytest.raises(Forbidden):
        manager.insert_many([NotASchema(name="x")])  # type: ignore[list-item]


# --- delete_many ---


@pytest.mark.usefixtures("items")
def test_delete_many(manager: Manager):
    deleted = manager.delete_many(Item, filter=Item.category == "fruit")
    assert deleted == 2
    assert manager.count(Item) == 3


@pytest.mark.usefixtures("items")
def test_delete_many_all(manager: Manager):
    deleted = manager.delete_many(Item)
    assert deleted == 5


@pytest.mark.usefixtures("items")
def test_delete_many_no_match(manager: Manager):
    deleted = manager.delete_many(Item, filter=Item.category == "seafood")
    assert deleted == 0


# --- update_many ---


@pytest.mark.usefixtures("items")
def test_update_many(manager: Manager):
    updated = manager.update_many(
        Item,
        filter=Item.category == "fruit",
        update={"$set": {"price": 99}},
    )
    assert updated == 2
    apple = manager.get(Item, filter=Item.id == 1)
    assert apple.price == 99


@pytest.mark.usefixtures("items")
def test_update_many_no_filter(manager: Manager):
    updated = manager.update_many(
        Item,
        update={"$set": {"category": "all"}},
    )
    assert updated == 5


@pytest.mark.usefixtures("items")
def test_update_many_no_match(manager: Manager):
    updated = manager.update_many(
        Item,
        filter=Item.category == "seafood",
        update={"$set": {"price": 0}},
    )
    assert updated == 0


# --- distinct ---


@pytest.mark.usefixtures("items")
def test_distinct(manager: Manager):
    categories = manager.distinct(Item, field="category")
    assert sorted(categories) == ["fruit", "pastry", "vegetable"]


@pytest.mark.usefixtures("items")
def test_distinct_with_filter(manager: Manager):
    categories = manager.distinct(
        Item, field="category", filter=Item.price >= 4
    )
    assert sorted(categories) == ["pastry"]


def test_distinct_empty(manager: Manager):
    categories = manager.distinct(Item, field="category")
    assert categories == []
