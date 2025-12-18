import pytest

from strata.expressions import Month


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Month("$date")
        result = op.compile_expression(context=context)
        assert result == {"$month": {"date": "$date"}}
