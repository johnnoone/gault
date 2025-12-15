import pytest
from strata.expressions import (
    CompilationError,
    Literal,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Literal("$var")
        result = compile_expression(op, context=context)
        assert result == {
            "$literal": "$var",
        }


def test_query(context, subtests: pytest.Subtests):
    op = Literal("$var")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
