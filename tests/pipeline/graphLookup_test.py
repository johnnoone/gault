from gault import Model
from gault.pipelines import Pipeline


def test_graph_lookup():
    class MyModel(Model, collection="my-coll"):
        pass

    pipeline = Pipeline()
    pipeline = pipeline.graph_lookup(
        MyModel,
        start_with="$reportsTo",
        local_field="reportsTo",
        foreign_field="name",
        into="reportingHierarchy",
    )
    result = pipeline.build()
    assert result == [
        {
            "$graphLookup": {
                "from": "my-coll",
                "startWith": "$reportsTo",
                "connectFromField": "reportsTo",
                "connectToField": "name",
                "as": "reportingHierarchy",
            }
        }
    ]
