import pytest
from strata.expressions import (
    CompilationError,
    SubStrBytes,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SubStrBytes("$input1", "$index", "$count")
        result = compile_expression(op, context=context)
        assert result == {
            "$substrBytes": ["$input1", "$index", "$count"],
        }


def test_query(context, subtests: pytest.Subtests):
    op = SubStrBytes("$input1", "$index", "$count")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
