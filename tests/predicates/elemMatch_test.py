from gault.predicates import ElemMatch, Ne


def test_compile_unwrapped(context):
    predicate = ElemMatch(
        {"field1": {"$eq": "value1"}},
        {"field2": {"$eq": "value2"}},
        Ne("foo"),
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$elemMatch": {
            "field1": {"$eq": "value1"},
            "field2": {"$eq": "value2"},
            "$ne": "foo",
        }
    }


def test_compile_wrapped(context):
    predicate = ElemMatch(
        [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
            Ne("foo"),
        ]
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$elemMatch": {
            "field1": {"$eq": "value1"},
            "field2": {"$eq": "value2"},
            "$ne": "foo",
        }
    }
