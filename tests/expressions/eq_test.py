import pytest

from gault.expressions import Eq


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Eq("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$eq": ["field", "value"]}

    with subtests.test():
        op = Eq("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$eq": ["field", "$value"]}
