import pytest
from strata.expressions import Lt, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Lt("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$lt": ["field", "value"]}

    with subtests.test():
        op = Lt("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$lt": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Lt("field", "value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$lt": "value"}}

    with subtests.test():
        op = Lt("field", "$value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$lt": "$value"}}
