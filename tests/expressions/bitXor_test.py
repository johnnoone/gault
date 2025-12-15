import pytest
from strata.expressions import (
    BitXor,
    CompilationError,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BitXor("$a", "$b")
        result = compile_expression(op, context=context)
        assert result == {"$bitXor": ["$a", "$b"]}

    with subtests.test():
        op = BitXor("$a", 42)
        result = compile_expression(op, context=context)
        assert result == {"$bitXor": ["$a", 42]}


def test_query(context, subtests: pytest.Subtests):
    op = BitXor("$binary")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
