from typing import Any, Mapping

import pytest

from gault import AsyncManager, Attribute, Pipeline, Schema, configure
from gault.accumulators import Sum
from gault.predicates import Field


class MyModel(Schema, collection="my-coll"):
    id: Attribute[int]
    name: Attribute[str]
    tags: Attribute[list[str]]
    number: Attribute[int]
    reports_to: Attribute[str | None] = configure(default=None, db_alias="reportsTo")


class Reporter(Schema, collection="my-coll"):
    name: Attribute[str]
    report_to: Attribute[str | None] = configure(
        default=None,
        db_alias="reportsTo",
    )
    reporting_hierarchy: Attribute[dict | None] = configure(
        default=None,
        db_alias="reportingHierarchy",
    )


class Sized(Schema, collection="my-coll"):
    name: Attribute[str]
    size: str


class MyProjection(Schema, collection="my-coll"):
    name: Attribute[str]


class MyBucket(Schema, collection="my-coll"):
    bucket: Attribute[Any]
    count: Attribute[int]


class Total(Schema, collection="my-coll"):
    count: Attribute[int]


class UnwindByTag(Schema, collection="my-coll"):
    name: Attribute[str]
    tag: Attribute[str]


class Facet(Schema, collection="my-coll"):
    total: Attribute[int]
    count: Attribute[int]
    avg: Attribute[float]


@pytest.fixture(autouse=True, name="instances")
async def get_instances(manager: AsyncManager):
    instances = [
        MyModel(id=1, name="ghost", tags=["blue", "red"], number=1),
        MyModel(
            id=2,
            name="established",
            tags=["blue", "red", "green"],
            number=10,
            reports_to="ghost",
        ),
        MyModel(
            id=3, name="mathematics", tags=["red"], number=100, reports_to="established"
        ),
        MyModel(
            id=4, name="unit", tags=["red"], number=1_000, reports_to="established"
        ),
        MyModel(id=5, name="basic", tags=["red"], number=1, reports_to="mathematics"),
        MyModel(id=6, name="poetry", tags=["green"], number=10, reports_to="unit"),
        MyModel(id=7, name="culture", tags=["red", "green"], number=100),
        MyModel(id=8, name="embarrassment", tags=["red", "green"], number=1_000),
        MyModel(id=9, name="chest", tags=["yellow"], number=1),
        MyModel(id=10, name="calorie", tags=["yellow"], number=10),
        MyModel(id=11, name="wonder", tags=["blue", "red"], number=100),
        MyModel(id=12, name="peace", tags=["blue", "red", "green"], number=1_000),
        MyModel(id=13, name="simplicity", tags=["red"], number=1),
        MyModel(id=14, name="embryo", tags=["red"], number=10),
        MyModel(id=15, name="privacy", tags=["red"], number=100),
        MyModel(id=16, name="decade", tags=["green"], number=1_000),
        MyModel(id=17, name="achieve", tags=["red", "green"], number=1),
        MyModel(id=18, name="slip", tags=["red", "green"], number=10),
        MyModel(id=19, name="need", tags=["yellow"], number=100),
        MyModel(id=20, name="symptom", tags=["yellow"], number=1_000),
    ]
    for instance in instances:
        await manager.insert(instance)
    return instances


async def test_match_query(manager: AsyncManager, instances):
    query = {"tags": "yellow"}
    pipeline = Pipeline().match(query)
    iterator = manager.select(MyModel, pipeline)
    persisted = [instance async for instance in iterator]

    expected = [instance for instance in instances if "yellow" in instance.tags]
    assert persisted == expected


async def test_match_operator(manager: AsyncManager, instances):
    query = MyModel.tags == "yellow"
    pipeline = Pipeline().match(query)
    iterator = manager.select(MyModel, pipeline)
    persisted = [instance async for instance in iterator]

    expected = [instance for instance in instances if "yellow" in instance.tags]
    assert persisted == expected


async def test_skip(manager: AsyncManager, instances):
    number = 15
    pipeline = Pipeline().skip(number)
    iterator = manager.select(MyModel, pipeline)
    persisted = [instance async for instance in iterator]

    expected = instances[15:]
    assert persisted == expected


async def test_take(manager: AsyncManager, instances):
    number = 2
    pipeline = Pipeline().take(number)
    iterator = manager.select(MyModel, pipeline)
    persisted = [instance async for instance in iterator]

    expected = instances[:2]
    assert persisted == expected


async def test_sample(manager: AsyncManager, instances):
    number = 4
    pipeline = Pipeline().sample(number)
    iterator = manager.select(MyModel, pipeline)
    persisted = [instance async for instance in iterator]

    assert len(persisted) == 4
    for item in persisted:
        assert item in persisted


async def test_sort(manager: AsyncManager, instances, subtests):
    with subtests.test("Attribute.asc()"):
        pipeline = Pipeline().sort(MyModel.name.asc())
        iterator = manager.select(MyModel, pipeline)
        persisted = [instance async for instance in iterator]
        assert persisted == sorted(instances, key=lambda x: x.name)

    with subtests.test("Attribute.desc()"):
        pipeline = Pipeline().sort(MyModel.name.desc())
        iterator = manager.select(MyModel, pipeline)
        persisted = [instance async for instance in iterator]
        assert persisted == sorted(instances, key=lambda x: x.name, reverse=True)


async def test_project_model(manager: AsyncManager):
    pipeline = Pipeline().project(MyProjection).take(2)
    iterator = manager.select(MyProjection, pipeline)
    persisted = [instance async for instance in iterator]
    assert persisted == [
        MyProjection(name="ghost"),
        MyProjection(name="established"),
    ]


async def test_project_fields(manager: AsyncManager):
    pipeline = Pipeline().project({"name": {"$toUpper": "$name"}}).take(2)
    iterator = manager.select(MyProjection, pipeline)
    persisted = [instance async for instance in iterator]
    assert persisted == [
        MyProjection(name="GHOST"),
        MyProjection(name="ESTABLISHED"),
    ]


async def test_bucket(manager: AsyncManager):
    pipeline = (
        Pipeline()
        .bucket(
            {"count": Sum(1)},
            by="$number",
            boundaries=[0, 15, 50, 250],
            default="infinite",
        )
        .set({"bucket": "$_id"})
    )
    iterator = manager.select(MyBucket, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        MyBucket(bucket=0, count=10),
        MyBucket(bucket=50, count=5),
        MyBucket(bucket="infinite", count=5),
    ]


async def test_bucket_auto(manager: AsyncManager):
    pipeline = (
        Pipeline()
        .bucket_auto(
            {"count": Sum(1)},
            by="$number",
            buckets=3,
        )
        .set({"bucket": "$_id"})
    )
    iterator = manager.select(MyBucket, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        MyBucket(bucket={"min": 1, "max": 100}, count=10),
        MyBucket(bucket={"min": 100, "max": 1000}, count=10),
    ]


async def test_group(manager: AsyncManager):
    pipeline = (
        Pipeline()
        .group({"count": Sum(1)}, by="$number")
        .set({"bucket": "$_id"})
        .sort({"bucket": 1})
    )
    iterator = manager.select(MyBucket, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        MyBucket(bucket=1, count=5),
        MyBucket(bucket=10, count=5),
        MyBucket(bucket=100, count=5),
        MyBucket(bucket=1000, count=5),
    ]


async def test_set(manager: AsyncManager):
    spec: Mapping = {"name": {"$toUpper": "$name"}}
    pipeline = Pipeline().set(spec).take(2)
    iterator = manager.select(MyProjection, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        MyProjection(name="GHOST"),
        MyProjection(name="ESTABLISHED"),
    ]


async def test_unset(manager: AsyncManager):
    pipeline = Pipeline().unset("_id").take(2)
    iterator = manager.select(MyProjection, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        MyProjection(name="ghost"),
        MyProjection(name="established"),
    ]


async def test_unwind(manager: AsyncManager):
    pipeline = (
        Pipeline()
        .unwind("$tags")
        .match({"name": "ghost"})
        .set({"tag": "$tags"})
        .sort("tag")
    )
    iterator = manager.select(UnwindByTag, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        UnwindByTag(name="ghost", tag="blue"),
        UnwindByTag(name="ghost", tag="red"),
    ]


async def test_count(manager: AsyncManager, instances):
    pipeline = Pipeline().count("count")
    iterator = manager.select(Total, pipeline)
    persisted = [instance async for instance in iterator]
    assert persisted == [Total(count=len(instances))]


async def test_replace_with(manager: AsyncManager):
    pipeline = Pipeline().take(1).replace_with({"name": "my-name"})
    iterator = manager.select(MyProjection, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [MyProjection(name="my-name")]


async def test_union_with(manager: AsyncManager, instances):
    pipeline = Pipeline().union_with(MyModel).match({"id": instances[0].id})
    iterator = manager.select(MyModel, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        instances[0],
        instances[0],
    ]


async def test_graph_lookup(manager: AsyncManager):
    pipeline = (
        Pipeline()
        .match({"name": "basic"})
        .graph_lookup(
            Reporter,
            start_with="$reportsTo",
            local_field="reportsTo",
            foreign_field="name",
            # depth_field=...,
            # restrict_search_with_match=...,
            into="reportingHierarchy",
        )
        .set(
            {
                "reportingHierarchy": {
                    "$map": {
                        "input": "$reportingHierarchy",
                        "as": "hierarchy",
                        "in": {
                            "name": "$$hierarchy.name",
                            "reportsTo": "$$hierarchy.reportsTo",
                        },
                    }
                }
            }
        )
    )

    persisted = await manager.get(Reporter, pipeline)
    assert persisted.name == "basic"
    assert persisted.report_to == "mathematics"
    assert {  # type: ignore[operator]
        "name": "established",
        "reportsTo": "ghost",
    } in persisted.reporting_hierarchy
    assert {  # type: ignore[operator]
        "name": "mathematics",
        "reportsTo": "established",
    } in persisted.reporting_hierarchy
    assert {  # type: ignore[operator]
        "name": "ghost",
        "reportsTo": None,
    } in persisted.reporting_hierarchy


async def test_lookup(manager: AsyncManager):
    spec = (
        Pipeline()
        .documents(
            [
                {"modelId": 1, "size": "small"},
                {"modelId": 2, "size": "medium"},
                {"modelId": 3, "size": "large"},
            ]
        )
        .project({"size": True})
    )
    pipeline = (
        Pipeline()
        .match({"id": 1})
        .lookup(
            spec,
            local_field=Field("id"),
            foreign_field=Field("modelId"),
            into="sizes",
        )
        .set({"size": {"$first": "$sizes"}})
        .set({"size": "$size.size"})
    )
    iterator = manager.select(Sized, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        Sized(name="ghost", size="small"),
    ]


async def test_facet(manager: AsyncManager):
    pipeline = (
        Pipeline()
        .facet(
            {
                "count": Pipeline().count("value"),
                "total": Pipeline().group({"value": Sum("$number")}, by=None),
                "avg": Pipeline().group({"value": {"$avg": "$number"}}, by=None),
            }
        )
        .project(
            {
                "count": {
                    "$getField": {
                        "input": {"$arrayElemAt": ["$count", 0]},
                        "field": "value",
                    }
                },
                "total": {
                    "$getField": {
                        "input": {"$arrayElemAt": ["$total", 0]},
                        "field": "value",
                    }
                },
                "avg": {
                    "$getField": {
                        "input": {"$arrayElemAt": ["$avg", 0]},
                        "field": "value",
                    }
                },
            }
        )
    )
    iterator = manager.select(Facet, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        Facet(total=5555, count=20, avg=277.75),
    ]


async def test_documents(manager: AsyncManager):
    pipeline = Pipeline.documents([{"bucket": 1, "count": 1}])
    iterator = manager.select(MyBucket, pipeline)
    persisted = [instance async for instance in iterator]

    assert persisted == [
        MyBucket(bucket=1, count=1),
    ]
