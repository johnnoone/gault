import pytest
from strata.expressions import (
    CompilationError,
    Second,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Second("$date")
        result = compile_expression(op, context=context)
        assert result == {"$second": {"date": "$date"}}


def test_query(context, subtests: pytest.Subtests):
    op = Second("$date")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
