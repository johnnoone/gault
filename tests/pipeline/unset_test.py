from gault.pipelines import Pipeline


def test_declared_fields():
    pipeline = Pipeline()
    pipeline = pipeline.unset("attr1")
    result = pipeline.build()
    assert result == [
        {
            "$unset": ["attr1"],
        },
    ]


def test_missing_fields():
    pipeline = Pipeline()
    pipeline = pipeline.unset()
    result = pipeline.build()
    assert result == []
