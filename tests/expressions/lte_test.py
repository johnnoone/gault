import pytest

from strata.expressions import Lte, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Lte("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$lte": ["field", "value"]}

    with subtests.test():
        op = Lte("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$lte": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Lte("field", "value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$lte": "value"}}

    with subtests.test():
        op = Lte("field", "$value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$lte": "$value"}}
