from gault import accumulators
from gault.pipelines import Pipeline


def test_list_accumulators() -> None:
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


def test_mapping_accumulators() -> None:
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


def test_mapping_accumulators_expressions() -> None:
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


def test_spread_accumulators() -> None:
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
