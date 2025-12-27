from gault.pipelines import CollectionPipeline, Pipeline


def test_pipeline_based():
    pipeline = Pipeline()
    pipeline = pipeline.union_with(CollectionPipeline("other"))
    result = pipeline.build()
    assert result == [
        {
            "$unionWith": {
                "coll": "other",
                "pipeline": [],
            },
        }
    ]
