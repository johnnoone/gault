import pytest

from strata.expressions import Trim


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Trim("$one", chars="$chars")
        result = op.compile_expression(context=context)
        assert result == {"$trim": {"chars": "$chars", "input": "$one"}}
