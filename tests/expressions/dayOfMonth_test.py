import pytest

from gault.expressions import DayOfMonth


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DayOfMonth("$date")
        result = op.compile_expression(context=context)
        assert result == {"$dayOfMonth": {"date": "$date"}}
