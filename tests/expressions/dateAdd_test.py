from datetime import datetime

import pytest

from strata.expressions import DateAdd


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateAdd(
            datetime.fromisoformat("2020-11-30T12:10:05Z"),
            unit="month",
            amount=1,
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateAdd": {
                "startDate": datetime.fromisoformat("2020-11-30T12:10:05Z"),
                "unit": "month",
                "amount": 1,
            }
        }

    with subtests.test():
        op = DateAdd(
            "$login",
            unit="day",
            amount=1,
            timezone="$location",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateAdd": {
                "startDate": "$login",
                "unit": "day",
                "amount": 1,
                "timezone": "$location",
            }
        }
