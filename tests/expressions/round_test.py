import pytest

from strata.expressions import Round


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Round("$var")
        result = op.compile_expression(context=context)
        assert result == {
            "$round": ["$var", 0],
        }
