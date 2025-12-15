
import pytest
from strata.expressions import (
    CompilationError,
    DateFromParts,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateFromParts(
            year=2017,
            month=0,
            day=1,
            hour=12,
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$dateFromParts": {
                "day": 1,
                "hour": 12,
                "month": 0,
                "year": 2017,
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = DateFromParts(
        year=2017,
        month=0,
        day=1,
        hour=12,
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
