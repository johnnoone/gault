from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.replace_with(
        {
            "attr1": True,
        }
    )
    result = pipeline.build()
    assert result == [
        {
            "$replaceWith": {
                "attr1": True,
            },
        }
    ]
