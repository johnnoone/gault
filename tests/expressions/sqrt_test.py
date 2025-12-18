import pytest

from strata.expressions import Sqrt


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Sqrt("$input")
        result = op.compile_expression(context=context)
        assert result == {"$sqrt": "$input"}
