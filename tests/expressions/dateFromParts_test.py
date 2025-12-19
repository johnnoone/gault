import pytest

from gault.expressions import DateFromParts


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateFromParts(
            year=2017,
            month=0,
            day=1,
            hour=12,
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateFromParts": {
                "day": 1,
                "hour": 12,
                "month": 0,
                "year": 2017,
            }
        }
