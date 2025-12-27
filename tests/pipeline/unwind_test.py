from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.unwind("$attr1")
    result = pipeline.build()
    assert result == [
        {
            "$unwind": {
                "path": "$attr1",
            }
        },
    ]
