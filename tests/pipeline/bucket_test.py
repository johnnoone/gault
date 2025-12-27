from gault.pipelines import Pipeline
from gault.predicates import Field
from gault.accumulators import Sum


def test_mapping_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket(
        {
            "count": {"$sum": 1},
        },
        by=Field("year_born"),
        boundaries=[1840, 1850, 1860, 1870, 1880],
        default="other",
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


def test_spread_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket(
        Sum(1).alias("count"),
        by=Field("year_born"),
        boundaries=[1840, 1850, 1860, 1870, 1880],
        default="other",
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


def test_list_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket(
        [
            Sum(1).alias("count"),
        ],
        by=Field("year_born"),
        boundaries=[1840, 1850, 1860, 1870, 1880],
        default="other",
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


def test_no_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket(
        by=Field("year_born"),
        boundaries=[1840, 1850, 1860, 1870, 1880],
        default="other",
    )
    result = pipeline.build()

    assert result == [
        {
            "$bucket": {
                "groupBy": "$year_born",
                "boundaries": [1840, 1850, 1860, 1870, 1880],
                "default": "other",
            }
        }
    ]
