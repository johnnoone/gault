import pytest

from strata.expressions import DateToParts


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateToParts(
            date="$date",
            timezone="$timezone",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$dateToParts": {
                "date": "$date",
                "timezone": "$timezone",
            }
        }
