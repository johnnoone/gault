from gault.pipelines import Pipeline
from gault.predicates import Field


def test_mapping_fields():
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


def test_list_fields():
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


def test_spread_fields():
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


def test_missing_fields():
    pipeline = Pipeline()
    pipeline = pipeline.set()
    result = pipeline.build()
    assert result == []
