import pytest
from strata.expressions import (
    CompilationError,
    DateToString,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateToString(
            date="$date",
            timezone="$timezone",
            on_null="$date",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$dateToString": {
                "date": "$date",
                "timezone": "$timezone",
                "onNull": "$date",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = DateToString(
        date="$date",
        timezone="$timezone",
        on_null="$date",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
