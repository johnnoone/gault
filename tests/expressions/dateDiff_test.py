from datetime import datetime

import pytest

from strata.expressions import DateDiff


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateDiff(
            datetime.fromisoformat("2020-11-30T12:10:05Z"),
            "$delivered",
            unit="month",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateDiff": {
                "startDate": datetime.fromisoformat("2020-11-30T12:10:05Z"),
                "endDate": "$delivered",
                "unit": "month",
            }
        }
