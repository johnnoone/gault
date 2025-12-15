import pytest
from strata.expressions import (
    CompilationError,
    StrLenCP,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = StrLenCP("$input")
        result = compile_expression(op, context=context)
        assert result == {"$strLenCP": "$input"}


def test_query(context, subtests: pytest.Subtests):
    op = StrLenCP("$input")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
