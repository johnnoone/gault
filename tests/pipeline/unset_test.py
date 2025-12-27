from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.unset("attr1")
    result = pipeline.build()
    assert result == [
        {
            "$unset": ["attr1"],
        },
    ]
