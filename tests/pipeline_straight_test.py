from gault import Attribute, Model, Schema, accumulators
from gault.expressions import Var
from gault.pipelines import CollectionPipeline, Pipeline
from gault.predicates import Field


def test_pipe():
    pipeline = Pipeline()
    pipeline = pipeline.raw({"$before": True})
    pipeline = pipeline.pipe(lambda p: p.raw({"$pipe": True}))
    pipeline = pipeline.raw({"$after": True})
    result = pipeline.build()
    assert result == [
        {"$before": True},
        {"$pipe": True},
        {"$after": True},
    ]


class TestMatch:
    def test_reqular(self, subtests):
        # TODO: match operator
        # TODO: match query predicate

        pipeline = Pipeline()
        pipeline = pipeline.match({"attr1": True, "attr2": False})
        result = pipeline.build()
        assert result == [
            {
                "$match": {
                    "attr1": True,
                    "attr2": False,
                },
            },
        ]

    def test_operator(self, subtests):
        class MyModel(Model, collection="coll"):
            id: Attribute[str]
            age: Attribute[int]
            name: Attribute[str]

        query = (
            MyModel.id.eq("foo")
            & MyModel.age.in_([1, 2, 3])
            & MyModel.name.ne(Var("other"))
        )

        pipeline = Pipeline()
        pipeline = pipeline.match(query)
        result = pipeline.build()
        assert result == [
            {
                "$match": {
                    "$and": [
                        {"id": {"$eq": "foo"}},
                        {"age": {"$in": [1, 2, 3]}},
                        {"name": {"$ne": "$$other"}},
                    ],
                }
            },
        ]

    def test_query(self, subtests):
        query = (
            Field("id").eq("foo")
            & Field("age").in_(1, 2, 3)
            & Field("name").ne(Var("other"))
        )

        pipeline = Pipeline()
        pipeline = pipeline.match(query)
        result = pipeline.build()
        assert result == [
            {
                "$match": {
                    "$and": [
                        {"id": {"$eq": "foo"}},
                        {"age": {"$in": [1, 2, 3]}},
                        {"name": {"$ne": "$$other"}},
                    ],
                }
            },
        ]


def test_skip():
    pipeline = Pipeline()
    pipeline = pipeline.skip(10)
    result = pipeline.build()
    assert result == [
        {"$skip": 10},
    ]


def test_take():
    pipeline = Pipeline()
    pipeline = pipeline.take(10)
    result = pipeline.build()
    assert result == [
        {"$limit": 10},
    ]


def test_sample():
    pipeline = Pipeline()
    pipeline = pipeline.sample(10)
    result = pipeline.build()
    assert result == [
        {
            "$sample": {"size": 10},
        },
    ]


def test_sort():
    pipeline = Pipeline()
    pipeline = pipeline.sort("name")
    result = pipeline.build()
    assert result == [
        {
            "$sort": {"name": 1},
        },
    ]


def test_project_dict_projection(subtests):
    with subtests.test("dict projection"):
        pipeline = Pipeline()
        pipeline = pipeline.project(
            {
                "attr1": True,
                "attr2": False,
                Field("attr3"): True,
            }
        )
        result = pipeline.build()
        assert result == [
            {
                "$project": {
                    "_id": False,
                    "attr1": True,
                    "attr2": False,
                    "attr3": True,
                }
            },
        ]


def test_project_wrapped_projection(subtests):
    with subtests.test("list projection"):
        pipeline = Pipeline()
        pipeline = pipeline.project(
            Field("attr1").keep(),
            Field("attr2").keep(),
            Field("attr3").keep(alias="my_alias"),
            Field("attr4").remove(),
            Field("attr5").assign(input="Some Value"),
        )
        result = pipeline.build()
        assert result == [
            {
                "$project": {
                    "_id": False,
                    "attr1": True,
                    "attr2": True,
                    "my_alias": "$attr3",
                    "attr4": "$$REMOVE",
                    "attr5": "Some Value",
                }
            },
        ]


def test_project_list_projection(subtests):
    with subtests.test("wrapped projection"):
        pipeline = Pipeline()
        pipeline = pipeline.project(
            [
                Field("attr1").keep(),
                Field("attr2").keep(),
                Field("attr3").keep(alias="my_alias"),
                Field("attr4").remove(),
                Field("attr5").assign(input="Some Value"),
            ]
        )
        result = pipeline.build()
        assert result == [
            {
                "$project": {
                    "_id": False,
                    "attr1": True,
                    "attr2": True,
                    "my_alias": "$attr3",
                    "attr4": "$$REMOVE",
                    "attr5": "Some Value",
                }
            },
        ]

    with subtests.test("project schema"):

        class MySchema(Schema, collection="my"):
            id: str
            name: str

        pipeline = Pipeline()
        pipeline = pipeline.project(MySchema)
        result = pipeline.build()
        assert result == [
            {
                "$project": {
                    "_id": False,
                    "id": True,
                    "name": True,
                }
            },
        ]

    with subtests.test("project model"):

        class MyModel(Model, collection="my"):
            id: str
            name: str

        pipeline = Pipeline()
        pipeline = pipeline.project(MyModel)
        result = pipeline.build()
        assert result == [
            {
                "$project": {
                    "_id": False,
                    "id": True,
                    "name": True,
                }
            },
        ]


def test_bucket():
    pipeline = Pipeline()
    pipeline = pipeline.bucket(
        Field("year_born"),
        boundaries=[1840, 1850, 1860, 1870, 1880],
        default="other",
        output={
            "count": {"$sum": 1},
        },
    )
    result = pipeline.build()

    assert result == [
        {
            "$bucket": {
                "groupBy": "$year_born",
                "boundaries": [1840, 1850, 1860, 1870, 1880],
                "default": "other",
                "output": {"count": {"$sum": 1}},
            }
        }
    ]


def test_bucket_auto():
    pipeline = Pipeline()
    pipeline = pipeline.bucket_auto(
        "$_id",
        buckets=3,
        output={
            "count": {"$sum": 1},
            "years": {"$push": "$year"},
        },
        granularity="1-2-5",
    )
    result = pipeline.build()
    assert result == [
        {
            "$bucketAuto": {
                "groupBy": "$_id",
                "buckets": 3,
                "output": {
                    "count": {"$sum": 1},
                    "years": {"$push": "$year"},
                },
                "granularity": "1-2-5",
            }
        }
    ]


def test_group_list() -> None:
    pipeline = Pipeline()
    pipeline = pipeline.group(
        [
            accumulators.Sum(1).alias("total"),
        ],
        by="$_id",
    )
    result = pipeline.build()
    assert result == [
        {
            "$group": {
                "_id": "$_id",
                "total": {"$sum": 1},
            },
        },
    ]


def test_group_mapping() -> None:
    pipeline = Pipeline()
    pipeline = pipeline.group(
        {
            "total": accumulators.Sum(1),
        },
        by="$_id",
    )
    result = pipeline.build()
    assert result == [
        {
            "$group": {
                "_id": "$_id",
                "total": {"$sum": 1},
            },
        },
    ]


def test_group_expressions() -> None:
    pipeline = Pipeline()
    pipeline = pipeline.group(
        {
            "total": {"$sum": 1},
        },
        by="$_id",
    )
    result = pipeline.build()
    assert result == [
        {
            "$group": {
                "_id": "$_id",
                "total": {"$sum": 1},
            },
        },
    ]


def test_group_spread() -> None:
    pipeline = Pipeline()
    pipeline = pipeline.group(
        accumulators.Sum(1).alias("total"),
        by="$_id",
    )
    result = pipeline.build()
    assert result == [
        {
            "$group": {
                "_id": "$_id",
                "total": {"$sum": 1},
            },
        },
    ]


def test_set_field():
    pipeline = Pipeline()
    pipeline = pipeline.set_field("attr1", "value")
    result = pipeline.build()
    assert result == [
        {
            "$set": {
                "attr1": "value",
            }
        },
    ]


def test_set_mapping():
    pipeline = Pipeline()
    pipeline = pipeline.set(
        {
            "attr1": "value",
        }
    )
    result = pipeline.build()
    assert result == [
        {
            "$set": {
                "attr1": "value",
            }
        },
    ]


def test_set_list():
    pipeline = Pipeline()
    pipeline = pipeline.set(
        [
            Field("attr1").assign("value"),
        ]
    )
    result = pipeline.build()
    assert result == [
        {
            "$set": {
                "attr1": "value",
            }
        },
    ]


def test_set_unwrapped():
    pipeline = Pipeline()
    pipeline = pipeline.set(
        Field("attr1").assign("value"),
    )
    result = pipeline.build()
    assert result == [
        {
            "$set": {
                "attr1": "value",
            }
        },
    ]


def test_unset():
    pipeline = Pipeline()
    pipeline = pipeline.unset("attr1")
    result = pipeline.build()
    assert result == [
        {
            "$unset": ["attr1"],
        },
    ]


def test_unwind():
    pipeline = Pipeline()
    pipeline = pipeline.unwind("$attr1")
    result = pipeline.build()
    assert result == [
        {
            "$unwind": {
                "path": "$attr1",
            }
        },
    ]


def test_count():
    pipeline = Pipeline()
    pipeline = pipeline.count("total")
    result = pipeline.build()
    assert result == [
        {
            "$count": "total",
        },
    ]


def test_replace_with():
    pipeline = Pipeline()
    pipeline = pipeline.replace_with(
        {
            "attr1": True,
        }
    )
    result = pipeline.build()
    assert result == [
        {
            "$replaceWith": {
                "attr1": True,
            },
        }
    ]


def test_union_with():
    pipeline = Pipeline()
    pipeline = pipeline.union_with(CollectionPipeline("other"))
    result = pipeline.build()
    assert result == [
        {
            "$unionWith": {
                "coll": "other",
                "pipeline": [],
            },
        }
    ]


def test_graph_lookup():
    class MyModel(Model, collection="my-coll"):
        pass

    pipeline = Pipeline()
    pipeline = pipeline.graph_lookup(
        MyModel,
        start_with="$reportsTo",
        local_field="reportsTo",
        foreign_field="name",
        into="reportingHierarchy",
    )
    result = pipeline.build()
    assert result == [
        {
            "$graphLookup": {
                "from": "my-coll",
                "startWith": "$reportsTo",
                "connectFromField": "reportsTo",
                "connectToField": "name",
                "as": "reportingHierarchy",
            }
        }
    ]


def test_lookup_model_based():
    class MyModel(Model, collection="my-coll-model"):
        pass

    pipeline = Pipeline()
    pipeline = pipeline.lookup(MyModel, into="joined")
    result = pipeline.build()
    assert result == [
        {
            "$lookup": {
                "from": "my-coll-model",
                "as": "joined",
            }
        }
    ]


def test_lookup_pipeline_based():
    sub = CollectionPipeline("sub-collection").match({"number": 42})

    pipeline = Pipeline()
    pipeline = pipeline.lookup(sub, into=Field("joined"))
    result = pipeline.build()
    assert result == [
        {
            "$lookup": {
                "from": "sub-collection",
                "as": "joined",
                "pipeline": [
                    {
                        "$match": {
                            "number": 42,
                        }
                    }
                ],
            }
        }
    ]


def test_facet():
    pipeline = Pipeline()
    pipeline = pipeline.facet({"foo": Pipeline().match(Field("attr").eq(1))})
    result = pipeline.build()
    assert result == [
        {
            "$facet": {
                "foo": [
                    {
                        "$match": {
                            "attr": {"$eq": 1},
                        }
                    },
                ],
            },
        },
    ]


def test_raw():
    pipeline = Pipeline()
    pipeline = pipeline.raw(
        {
            "$custom-value": "this-is-custom-value",
        }
    )
    result = pipeline.build()
    assert result == [
        {
            "$custom-value": "this-is-custom-value",
        },
    ]


def test_build():
    pipeline = Pipeline()
    result = pipeline.build()
    assert result == []


def test_documents(subtests):
    with subtests.test():
        pipeline = Pipeline.documents(
            {"id": 1},
            {"id": 2},
            {"id": 3},
        )
        result = pipeline.build()
        assert result == [
            {
                "$documents": [
                    {"id": 1},
                    {"id": 2},
                    {"id": 3},
                ]
            },
        ]

    with subtests.test():
        pipeline = Pipeline.documents(
            [
                {"id": 1},
                {"id": 2},
                {"id": 3},
            ]
        )
        result = pipeline.build()
        assert result == [
            {
                "$documents": [
                    {"id": 1},
                    {"id": 2},
                    {"id": 3},
                ]
            },
        ]
