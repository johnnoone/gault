from gault.accumulators import Push, Sum
from gault.pipelines import Pipeline


def test_mapping_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket_auto(
        {
            "count": {"$sum": 1},
            "years": {"$push": "$year"},
        },
        by="$_id",
        buckets=3,
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


def test_spread_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket_auto(
        Sum(1).alias("count"),
        Push("$year").alias("years"),
        by="$_id",
        buckets=3,
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


def test_list_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket_auto(
        [
            Sum(1).alias("count"),
            Push("$year").alias("years"),
        ],
        by="$_id",
        buckets=3,
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


def test_no_output():
    pipeline = Pipeline()
    pipeline = pipeline.bucket_auto(
        None,
        by="$_id",
        buckets=3,
        granularity="1-2-5",
    )
    result = pipeline.build()
    assert result == [
        {
            "$bucketAuto": {
                "groupBy": "$_id",
                "buckets": 3,
                "granularity": "1-2-5",
            }
        }
    ]
