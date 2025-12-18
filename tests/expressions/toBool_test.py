import pytest

from strata.expressions import ToBool


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToBool("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toBool": "$one"}
