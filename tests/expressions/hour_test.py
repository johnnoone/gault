import pytest

from strata.expressions import Hour


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Hour("$date")
        result = op.compile_expression(context=context)
        assert result == {"$hour": {"date": "$date"}}
