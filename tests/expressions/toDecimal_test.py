import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    ToDecimal,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToDecimal("$one")
        result = compile_expression(op, context=context)
        assert result == {"$toDecimal": "$one"}


def test_query(context, subtests: pytest.Subtests):
    op = ToDecimal("$one")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
