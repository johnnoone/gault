import pytest

from gault.expressions import IsoDayOfWeek


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IsoDayOfWeek("$date")
        result = op.compile_expression(context=context)
        assert result == {"$isoDayOfWeek": {"date": "$date"}}
