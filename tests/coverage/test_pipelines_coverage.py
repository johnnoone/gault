from __future__ import annotations

import pytest

from gault import Attribute, Model
from gault.pipelines import (
    MatchStep,
    Pipeline,
)
from gault.predicates import Field


def test_match_no_args(context):
    """Line 147: Pipeline.match() with no args creates empty match."""
    pipeline = Pipeline()
    pipeline = pipeline.match()
    result = pipeline.build()
    assert result == [{"$match": {}}]


def test_project_with_model_instance(context):
    """Line 325: Pipeline.project() with Model instance extracts type."""

    class MyModel(Model, collection="coll"):
        id: Attribute[str]
        name: Attribute[str]

    instance = MyModel(id="1", name="foo")
    pipeline = Pipeline()
    pipeline = pipeline.project(instance)
    result = pipeline.build()
    assert result == [
        {
            "$project": {
                "_id": False,
                "id": True,
                "name": True,
            }
        }
    ]


def test_union_with_invalid_type():
    """Line 757: Pipeline.union_with with invalid type raises NotImplementedError."""
    pipeline = Pipeline()
    with pytest.raises(NotImplementedError):
        pipeline.union_with(int)


def test_lookup_invalid_parameter():
    """Line 872: Pipeline.lookup with invalid parameter raises NotImplementedError."""
    pipeline = Pipeline()
    with pytest.raises(NotImplementedError):
        pipeline.lookup(None, into="joined")


def test_raw_with_step():
    """Line 942: Pipeline.raw(Step) returns Step unchanged."""
    step = MatchStep(query={"status": "active"})
    pipeline = Pipeline()
    pipeline = pipeline.raw(step)
    result = pipeline.build()
    assert result == [{"$match": {"status": "active"}}]


def test_graph_lookup_with_depth_field(context):
    """Line 1223: GraphLookupStep with depth_field."""

    class MyModel(Model, collection="my-coll"):
        pass

    pipeline = Pipeline()
    pipeline = pipeline.graph_lookup(
        MyModel,
        start_with="$reportsTo",
        local_field="reportsTo",
        foreign_field="name",
        into="reportingHierarchy",
        depth_field="depth",
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
                "depthField": "depth",
            }
        }
    ]


def test_graph_lookup_with_restrict_search_with_match(context):
    """Line 1228: GraphLookupStep with restrict_search_with_match."""

    class MyModel(Model, collection="my-coll"):
        pass

    pipeline = Pipeline()
    pipeline = pipeline.graph_lookup(
        MyModel,
        start_with="$reportsTo",
        local_field="reportsTo",
        foreign_field="name",
        into="reportingHierarchy",
        restrict_search_with_match={"active": True},
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
                "restrictSearchWithMatch": {"active": True},
            }
        }
    ]


def test_unwind_with_include_array_index(context):
    """Line 1321: UnwindStep with include_array_index."""
    pipeline = Pipeline()
    pipeline = pipeline.unwind("$sizes", include_array_index=Field("arrayIndex"))
    result = pipeline.build()
    assert result == [
        {
            "$unwind": {
                "path": "$sizes",
                "includeArrayIndex": "$arrayIndex",
            }
        }
    ]
