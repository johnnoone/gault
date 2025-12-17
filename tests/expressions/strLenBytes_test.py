import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    StrLenBytes,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = StrLenBytes("$input")
        result = compile_expression(op, context=context)
        assert result == {"$strLenBytes": "$input"}


def test_query(context, subtests: pytest.Subtests):
    op = StrLenBytes("$input")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
