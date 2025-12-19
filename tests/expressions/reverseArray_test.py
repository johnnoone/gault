import pytest

from gault.expressions import ReverseArray


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ReverseArray("$var")
        result = op.compile_expression(context=context)
        assert result == {
            "$reverseArray": "$var",
        }
