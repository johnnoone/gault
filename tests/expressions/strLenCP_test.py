import pytest

from gault.expressions import StrLenCP


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = StrLenCP("$input")
        result = op.compile_expression(context=context)
        assert result == {"$strLenCP": "$input"}
