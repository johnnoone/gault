from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.sort("name")
    result = pipeline.build()
    assert result == [
        {
            "$sort": {"name": 1},
        },
    ]
