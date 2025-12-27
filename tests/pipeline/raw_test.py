from gault.pipelines import Pipeline


def test_render():
    pipeline = Pipeline()
    pipeline = pipeline.raw(
        {
            "$custom-value": "this-is-custom-value",
        }
    )
    result = pipeline.build()
    assert result == [
        {
            "$custom-value": "this-is-custom-value",
        },
    ]
