import pytest

from strata.expressions import Week


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Week("$date")
        result = op.compile_expression(context=context)
        assert result == {"$week": {"date": "$date"}}
