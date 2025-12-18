import pytest

from strata.expressions import ToUUID


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToUUID("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toUUID": "$one"}
