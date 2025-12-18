import pytest

from strata.expressions import Year


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Year("$date")
        result = op.compile_expression(context=context)
        assert result == {"$year": {"date": "$date"}}
