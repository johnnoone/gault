import pytest

from gault.expressions import Second


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Second("$date")
        result = op.compile_expression(context=context)
        assert result == {"$second": {"date": "$date"}}
