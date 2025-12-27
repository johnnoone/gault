from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.take(10)
    result = pipeline.build()
    assert result == [
        {"$limit": 10},
    ]
