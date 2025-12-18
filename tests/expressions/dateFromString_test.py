import pytest

from strata.expressions import DateFromString


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateFromString(
            date_string="$date",
            timezone="$timezone",
            on_error="$date",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateFromString": {
                "dateString": "$date",
                "timezone": "$timezone",
                "onError": "$date",
            }
        }
