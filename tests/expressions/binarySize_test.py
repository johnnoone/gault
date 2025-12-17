import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    BinarySize,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BinarySize("abcde")
        result = compile_expression(op, context=context)
        assert result == {"$binarySize": "abcde"}

    with subtests.test():
        op = BinarySize("$binary")
        result = compile_expression(op, context=context)
        assert result == {"$binarySize": "$binary"}


def test_query(context, subtests: pytest.Subtests):
    op = BinarySize("$binary")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
