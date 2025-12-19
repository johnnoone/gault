import pytest

from gault.expressions import Pow


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Pow(1, 2)
        result = op.compile_expression(context=context)
        assert result == {"$pow": [1, 2]}
