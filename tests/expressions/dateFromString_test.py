
import pytest
from strata.expressions import (
    CompilationError,
    DateFromString,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateFromString(
            date_string="$date",
            timezone="$timezone",
            on_error="$date",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$dateFromString": {
                "dateString": "$date",
                "timezone": "$timezone",
                "onError": "$date",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = DateFromString(
        date_string="$date",
        timezone="$timezone",
        on_error="$date",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
