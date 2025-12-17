import pytest

from strata.expressions import Gte, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Gte("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$gte": ["field", "value"]}

    with subtests.test():
        op = Gte("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$gte": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Gte("field", "value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$gte": "value"}}

    with subtests.test():
        op = Gte("field", "$value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$gte": "$value"}}
