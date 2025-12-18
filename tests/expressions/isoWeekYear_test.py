import pytest

from strata.expressions import IsoWeekYear


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IsoWeekYear("$date")
        result = op.compile_expression(context=context)
        assert result == {"$isoWeekYear": {"date": "$date"}}
