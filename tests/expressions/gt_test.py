import pytest

from gault.expressions import Gt


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Gt("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$gt": ["field", "value"]}

    with subtests.test():
        op = Gt("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$gt": ["field", "$value"]}
