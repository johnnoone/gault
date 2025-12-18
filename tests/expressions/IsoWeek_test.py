import pytest

from strata.expressions import IsoWeek


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IsoWeek("$date")
        result = op.compile_expression(context=context)
        assert result == {"$isoWeek": {"date": "$date"}}
