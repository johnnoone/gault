from gault import Model
from gault.pipelines import CollectionPipeline, Pipeline
from gault.predicates import Field


def test_lookup_model_based():
    class MyModel(Model, collection="my-coll-model"):
        pass

    pipeline = Pipeline()
    pipeline = pipeline.lookup(MyModel, into="joined")
    result = pipeline.build()
    assert result == [
        {
            "$lookup": {
                "from": "my-coll-model",
                "as": "joined",
            }
        }
    ]


def test_lookup_pipeline_based():
    sub = CollectionPipeline("sub-collection").match({"number": 42})

    pipeline = Pipeline()
    pipeline = pipeline.lookup(sub, into=Field("joined"))
    result = pipeline.build()
    assert result == [
        {
            "$lookup": {
                "from": "sub-collection",
                "as": "joined",
                "pipeline": [
                    {
                        "$match": {
                            "number": 42,
                        }
                    }
                ],
            }
        }
    ]
