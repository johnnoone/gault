from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.skip(10)
    result = pipeline.build()
    assert result == [
        {"$skip": 10},
    ]
