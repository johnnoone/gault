import pytest

from gault.expressions import Sigmoid


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Sigmoid("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$sigmoid": {"input": "$one", "onNull": "$two"}}
