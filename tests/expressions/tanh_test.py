import pytest

from strata.expressions import Tanh


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Tanh("$one")
        result = op.compile_expression(context=context)
        assert result == {"$tanh": "$one"}
