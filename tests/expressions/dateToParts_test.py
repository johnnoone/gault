
import pytest
from strata.expressions import (
    CompilationError,
    DateToParts,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateToParts(
            date="$date",
            timezone="$timezone",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$dateToParts": {
                "date": "$date",
                "timezone": "$timezone",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = DateToParts(
        date="$date",
        timezone="$timezone",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
