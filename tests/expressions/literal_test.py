import pytest

from strata.expressions import Literal


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Literal("$var")
        result = op.compile_expression(context=context)
        assert result == {
            "$literal": "$var",
        }
