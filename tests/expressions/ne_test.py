import pytest
from strata.expressions import Ne, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ne("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$ne": ["field", "value"]}

    with subtests.test():
        op = Ne("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$ne": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ne("field", "value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$ne": "value"}}

    with subtests.test():
        op = Ne("field", "$value")
        result = compile_query(op, context=context)
        assert result == {"field": {"$ne": "$value"}}
