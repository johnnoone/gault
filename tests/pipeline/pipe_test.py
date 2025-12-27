from gault.pipelines import Pipeline


def test_pipe():
    pipeline = Pipeline()
    pipeline = pipeline.raw({"$before": True})
    pipeline = pipeline.pipe(lambda p: p.raw({"$pipe": True}))
    pipeline = pipeline.raw({"$after": True})
    result = pipeline.build()
    assert result == [
        {"$before": True},
        {"$pipe": True},
        {"$after": True},
    ]
