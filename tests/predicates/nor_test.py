from strata.predicates import Nor


def test_compile_unwrapped(context):
    predicate = Nor(
        {"field1": {"$eq": "value1"}},
        {"field2": {"$eq": "value2"}},
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$nor": [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    }


def test_compile_wrapped(context):
    predicate = Nor(
        [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$nor": [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    }
