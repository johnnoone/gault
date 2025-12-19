import pytest

from gault.expressions import BinarySize


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BinarySize("abcde")
        result = op.compile_expression(context=context)
        assert result == {"$binarySize": "abcde"}

    with subtests.test():
        op = BinarySize("$binary")
        result = op.compile_expression(context=context)
        assert result == {"$binarySize": "$binary"}
