import pytest
from strata.expressions import (
    BitAnd,
    CompilationError,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BitAnd("$a", "$b")
        result = compile_expression(op, context=context)
        assert result == {"$bitAnd": ["$a", "$b"]}

    with subtests.test():
        op = BitAnd("$a", 42)
        result = compile_expression(op, context=context)
        assert result == {"$bitAnd": ["$a", 42]}


def test_query(context, subtests: pytest.Subtests):
    op = BitAnd("$a", "$b")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
