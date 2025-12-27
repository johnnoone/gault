from gault.pipelines import Pipeline
from gault.window_aggregators import Rank, Sum


def test_mapping_output():
    pipeline = Pipeline()
    pipeline = pipeline.set_window_fields(
        {
            "cumulativeSum": Sum("$amount"),
        },
        sort_by={"date": 1},
        partition_by="$category",
    )
    result = pipeline.build()
    assert result == [
        {
            "$setWindowFields": {
                "partitionBy": "$category",
                "sortBy": {"date": 1},
                "output": {
                    "cumulativeSum": {"$sum": "$amount"},
                },
            }
        }
    ]


def test_list_output():
    pipeline = Pipeline()
    pipeline = pipeline.set_window_fields(
        [
            Sum("$amount").alias("cumulativeSum"),
        ],
        sort_by={"date": 1},
    )
    result = pipeline.build()
    assert result == [
        {
            "$setWindowFields": {
                "sortBy": {"date": 1},
                "output": {
                    "cumulativeSum": {"$sum": "$amount"},
                },
            }
        }
    ]


def test_spread_output():
    pipeline = Pipeline()
    pipeline = pipeline.set_window_fields(
        Sum("$amount").alias("cumulativeSum"),
        Rank().alias("rank"),
        sort_by={"date": 1},
        partition_by="$category",
    )
    result = pipeline.build()
    assert result == [
        {
            "$setWindowFields": {
                "partitionBy": "$category",
                "sortBy": {"date": 1},
                "output": {
                    "cumulativeSum": {"$sum": "$amount"},
                    "rank": {"$rank": {}},
                },
            }
        }
    ]
