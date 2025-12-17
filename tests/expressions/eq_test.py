import pytest

from strata.expressions import Eq, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Eq("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$eq": ["field", "value"]}

    with subtests.test():
        op = Eq("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$eq": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Eq("field", "value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$eq": "value"}}

    with subtests.test():
        op = Eq("field", "$value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$eq": "$value"}}
