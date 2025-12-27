from gault.pipelines import Pipeline


def test_number_size():
    pipeline = Pipeline()
    pipeline = pipeline.take(10)
    result = pipeline.build()
    assert result == [
        {"$limit": 10},
    ]


def test_missing_size():
    pipeline = Pipeline()
    pipeline = pipeline.take(None)
    result = pipeline.build()
    assert result == []
