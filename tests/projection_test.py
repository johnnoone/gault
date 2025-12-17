import pytest

from strata.accumulators import Sum
from strata.exceptions import Forbidden
from strata.managers import AsyncManager
from strata.models import Model, Schema
from strata.pipelines import Pipeline


class MyModel(Schema, collection="my-coll"):
    id: int
    color: str


class ColorsCount(Model, collection="my-coll"):
    color: str
    count: int


@pytest.fixture(name="instances")
async def get_instances(manager: AsyncManager):
    instances = [
        MyModel(id=1, color="blue"),
        MyModel(id=2, color="blue"),
        MyModel(id=3, color="blue"),
        MyModel(id=4, color="blue"),
        MyModel(id=5, color="blue"),
        MyModel(id=6, color="blue"),
        MyModel(id=7, color="red"),
        MyModel(id=8, color="red"),
        MyModel(id=9, color="red"),
    ]

    for instance in instances:
        await manager.insert(instance)
    return instances


@pytest.mark.usefixtures("instances")
async def test_select(manager: AsyncManager):
    pipeline = Pipeline().group("$color", {"count": Sum(1)}).set({"color": "$_id"})
    result = {}
    async for instance in manager.select(ColorsCount, pipeline):
        result[instance.color] = instance
    assert result == {
        "red": ColorsCount(color="red", count=3),
        "blue": ColorsCount(color="blue", count=6),
    }


async def test_insert(manager: AsyncManager):
    with pytest.raises(Forbidden):
        await manager.insert(ColorsCount(color="green", count=1))


async def test_save(manager: AsyncManager):
    with pytest.raises(Forbidden):
        await manager.save(ColorsCount(color="green", count=1))
