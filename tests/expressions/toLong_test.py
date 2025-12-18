import pytest

from strata.expressions import ToLong


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToLong("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toLong": "$one"}
