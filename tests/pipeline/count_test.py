from gault.pipelines import Pipeline


def test_count():
    pipeline = Pipeline()
    pipeline = pipeline.count("total")
    result = pipeline.build()
    assert result == [
        {
            "$count": "total",
        },
    ]
