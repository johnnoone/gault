from __future__ import annotations

import pytest
from pymongo.asynchronous.database import AsyncDatabase

from gault.exceptions import Forbidden
from gault.managers import AsyncManager, Persistence
from gault.models import Attribute, Model, Schema, configure


class Item(Schema, collection="bulk-ops-collection"):
    id: Attribute[int] = configure(pk=True)
    name: Attribute[str]
    category: Attribute[str]
    price: Attribute[int]


class NotASchema(Model):
    name: Attribute[str]


@pytest.fixture(name="items")
async def get_items(database: AsyncDatabase, persistence: Persistence):
    await database.get_collection("bulk-ops-collection").insert_many(
        [
            {"id": 1, "name": "apple", "category": "fruit", "price": 1},
            {"id": 2, "name": "banana", "category": "fruit", "price": 2},
            {"id": 3, "name": "carrot", "category": "vegetable", "price": 3},
            {"id": 4, "name": "donut", "category": "pastry", "price": 5},
            {"id": 5, "name": "eclair", "category": "pastry", "price": 4},
        ]
    )


# --- insert_many ---


async def test_insert_many(manager: AsyncManager):
    items = [
        Item(id=10, name="fig", category="fruit", price=6),
        Item(id=11, name="grape", category="fruit", price=7),
        Item(id=12, name="ham", category="meat", price=10),
    ]
    result = await manager.insert_many(items)
    assert result == items
    assert await manager.count(Item) == 3


async def test_insert_many_marks_persisted(manager: AsyncManager):
    items = [
        Item(id=20, name="ice cream", category="dessert", price=5),
        Item(id=21, name="jam", category="spread", price=3),
    ]
    await manager.insert_many(items)
    for item in items:
        assert manager.persistence.is_persisted(item)


async def test_insert_many_empty(manager: AsyncManager):
    result = await manager.insert_many([])
    assert result == []


async def test_insert_many_non_schema_raises_forbidden(manager: AsyncManager):
    with pytest.raises(Forbidden):
        await manager.insert_many([NotASchema(name="x")])  # type: ignore[list-item]


# --- delete_many ---


@pytest.mark.usefixtures("items")
async def test_delete_many(manager: AsyncManager):
    deleted = await manager.delete_many(Item, filter=Item.category == "fruit")
    assert deleted == 2
    assert await manager.count(Item) == 3


@pytest.mark.usefixtures("items")
async def test_delete_many_all(manager: AsyncManager):
    deleted = await manager.delete_many(Item)
    assert deleted == 5


@pytest.mark.usefixtures("items")
async def test_delete_many_no_match(manager: AsyncManager):
    deleted = await manager.delete_many(Item, filter=Item.category == "seafood")
    assert deleted == 0


# --- update_many ---


@pytest.mark.usefixtures("items")
async def test_update_many(manager: AsyncManager):
    updated = await manager.update_many(
        Item,
        filter=Item.category == "fruit",
        update={"$set": {"price": 99}},
    )
    assert updated == 2
    apple = await manager.get(Item, filter=Item.id == 1)
    assert apple.price == 99


@pytest.mark.usefixtures("items")
async def test_update_many_no_filter(manager: AsyncManager):
    updated = await manager.update_many(
        Item,
        update={"$set": {"category": "all"}},
    )
    assert updated == 5


@pytest.mark.usefixtures("items")
async def test_update_many_no_match(manager: AsyncManager):
    updated = await manager.update_many(
        Item,
        filter=Item.category == "seafood",
        update={"$set": {"price": 0}},
    )
    assert updated == 0


# --- distinct ---


@pytest.mark.usefixtures("items")
async def test_distinct(manager: AsyncManager):
    categories = await manager.distinct(Item, field="category")
    assert sorted(categories) == ["fruit", "pastry", "vegetable"]


@pytest.mark.usefixtures("items")
async def test_distinct_with_filter(manager: AsyncManager):
    categories = await manager.distinct(
        Item, field="category", filter=Item.price >= 4
    )
    assert sorted(categories) == ["pastry"]


async def test_distinct_empty(manager: AsyncManager):
    categories = await manager.distinct(Item, field="category")
    assert categories == []
