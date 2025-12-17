import pytest

from strata.expressions import Not, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Not("field")
        result = compile_expression(op, context=context)
        assert result == {"$not": ["field"]}


def test_query(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Not("field")
        result = compile_query(op, context=context)
        assert result == {"$not": "field"}
