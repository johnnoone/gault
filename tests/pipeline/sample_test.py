from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.sample(10)
    result = pipeline.build()
    assert result == [
        {
            "$sample": {"size": 10},
        },
    ]
