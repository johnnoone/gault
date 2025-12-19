import pytest

from gault.expressions import DayOfWeek


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DayOfWeek("$date")
        result = op.compile_expression(context=context)
        assert result == {"$dayOfWeek": {"date": "$date"}}
