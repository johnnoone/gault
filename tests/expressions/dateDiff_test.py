from datetime import datetime

import pytest

from strata.compilers import CompilationError
from strata.expressions import DateDiff, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DateDiff(
            datetime.fromisoformat("2020-11-30T12:10:05Z"),
            "$delivered",
            unit="month",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$dateDiff": {
                "startDate": datetime.fromisoformat("2020-11-30T12:10:05Z"),
                "endDate": "$delivered",
                "unit": "month",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = DateDiff(
        datetime.fromisoformat("2020-11-30T12:10:05Z"),
        "$delivered",
        unit="month",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
