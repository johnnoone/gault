from gault.pipelines import Pipeline
from gault.predicates import Field


def test_mapping_facets():
    pipeline = Pipeline()
    pipeline = pipeline.facet(
        {
            "foo": Pipeline().match(Field("attr").eq(1)),
        }
    )
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


def test_list_facets():
    pipeline = Pipeline()
    pipeline = pipeline.facet(
        [
            Pipeline().match(Field("attr").eq(1)).alias("foo"),
        ]
    )
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


def test_spread_facets():
    pipeline = Pipeline()
    pipeline = pipeline.facet(
        Pipeline().match(Field("attr").eq(1)).alias("foo"),
    )
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
