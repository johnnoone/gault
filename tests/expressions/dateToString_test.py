import pytest

from gault.expressions import DateToString


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateToString(
            date="$date",
            timezone="$timezone",
            on_null="$date",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateToString": {
                "date": "$date",
                "timezone": "$timezone",
                "onNull": "$date",
            }
        }
