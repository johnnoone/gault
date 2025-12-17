from datetime import datetime

import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    DateAdd,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateAdd(
            datetime.fromisoformat("2020-11-30T12:10:05Z"),
            unit="month",
            amount=1,
        )
        result = compile_expression(op, context=context)
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
        result = compile_expression(op, context=context)
        assert result == {
            "$dateAdd": {
                "startDate": "$login",
                "unit": "day",
                "amount": 1,
                "timezone": "$location",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = DateAdd(
        "$login",
        unit="day",
        amount=1,
        timezone="$location",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
