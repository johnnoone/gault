import pytest
from strata.expressions import Gt, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Gt("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$gt": ["field", "value"]}

    with subtests.test():
        op = Gt("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$gt": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Gt("field", "value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$gt": "value"}}

    with subtests.test():
        op = Gt("field", "$value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$gt": "$value"}}
