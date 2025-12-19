import pytest

from gault.expressions import Multiply


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Multiply("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$multiply": ["field", "value"]}

    with subtests.test():
        op = Multiply("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$multiply": ["field", "$value"]}
