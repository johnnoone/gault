from gault.pipelines import Pipeline


def test_number_size():
    pipeline = Pipeline()
    pipeline = pipeline.skip(10)
    result = pipeline.build()
    assert result == [
        {"$skip": 10},
    ]


def test_missing_size():
    pipeline = Pipeline()
    pipeline = pipeline.skip(None)
    result = pipeline.build()
    assert result == []
