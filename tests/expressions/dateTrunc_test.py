from datetime import datetime

import pytest

from gault.expressions import DateTrunc


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateTrunc(
            datetime.fromisoformat("2020-11-30T12:10:05Z"),
            unit="month",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateTrunc": {
                "date": datetime.fromisoformat("2020-11-30T12:10:05Z"),
                "unit": "month",
            }
        }
