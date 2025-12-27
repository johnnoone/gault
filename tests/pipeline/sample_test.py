from gault.pipelines import Pipeline


def test_number_size():
    pipeline = Pipeline()
    pipeline = pipeline.sample(10)
    result = pipeline.build()
    assert result == [
        {
            "$sample": {"size": 10},
        },
    ]


def test_missing_size():
    pipeline = Pipeline()
    pipeline = pipeline.sample(None)
    result = pipeline.build()
    assert result == [], "sample must be discarded when size is missing"
