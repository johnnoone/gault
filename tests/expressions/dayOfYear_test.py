import pytest

from strata.expressions import DayOfYear


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DayOfYear("$date")
        result = op.compile_expression(context=context)
        assert result == {"$dayOfYear": {"date": "$date"}}
