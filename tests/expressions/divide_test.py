import pytest

from gault.expressions import Divide


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Divide("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$divide": ["field", "value"]}

    with subtests.test():
        op = Divide("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$divide": ["field", "$value"]}
