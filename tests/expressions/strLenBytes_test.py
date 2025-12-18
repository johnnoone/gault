import pytest

from strata.expressions import StrLenBytes


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = StrLenBytes("$input")
        result = op.compile_expression(context=context)
        assert result == {"$strLenBytes": "$input"}
