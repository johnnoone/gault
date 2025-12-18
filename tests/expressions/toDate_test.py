import pytest

from strata.expressions import ToDate


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToDate("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toDate": "$one"}
