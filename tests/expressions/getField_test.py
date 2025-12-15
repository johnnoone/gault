import pytest
from strata.expressions import (
    CompilationError,
    GetField,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = GetField(
            field={"$literal": "$small"},
            input="$quantity",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$getField": {
                "field": {"$literal": "$small"},
                "input": "$quantity",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = GetField(
        field={"$literal": "$small"},
        input="$quantity",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
