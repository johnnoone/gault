from strata.predicates import Or


def test_compile_unwrapped(context):
    predicate = Or(
        {"field1": {"$eq": "value1"}},
        {"field2": {"$eq": "value2"}},
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$or": [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    }


def test_compile_wrapped(context):
    predicate = Or(
        [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$or": [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    }
