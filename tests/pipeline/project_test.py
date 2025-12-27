from gault import Model, Schema
from gault.pipelines import Pipeline
from gault.predicates import Field


def test_mapping_projection(subtests):
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


def test_spread_projection(subtests):
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


def test_list_projection(subtests):
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


def test_schema_projection(subtests):
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


def test_model_projection(subtests):
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
