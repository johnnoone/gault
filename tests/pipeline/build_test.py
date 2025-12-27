from gault.pipelines import Pipeline


def test_build():
    pipeline = Pipeline()
    result = pipeline.build()
    assert result == []
