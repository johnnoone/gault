import pytest

from gault.expressions import Cmp


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Cmp("$qty", 250)
        result = op.compile_expression(context=context)
        assert result == {"$cmp": ["$qty", 250]}
