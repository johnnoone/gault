from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.set_field("attr1", "value")
    result = pipeline.build()
    assert result == [
        {
            "$set": {
                "attr1": "value",
            }
        },
    ]
