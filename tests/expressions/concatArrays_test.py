import pytest
from strata.expressions import (
    ConcatArrays,
    CompilationError,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ConcatArrays(["hello", " "], ["world"])
        result = compile_expression(op, context=context)
        assert result == {"$concatArrays": [["hello", " "], ["world"]]}


def test_query(context, subtests: pytest.Subtests):
    op = ConcatArrays(["hello", " "], ["world"])
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
