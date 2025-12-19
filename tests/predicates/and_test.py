from gault.predicates import And


def test_compile_unwrapped(context):
    predicate = And(
        {"field1": {"$eq": "value1"}},
        {"field2": {"$eq": "value2"}},
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$and": [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    }


def test_compile_wrapped(context):
    predicate = And(
        [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    )

    result = predicate.compile_query(context=context)
    assert result == {
        "$and": [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$eq": "value2"}},
        ]
    }
