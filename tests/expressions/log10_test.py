import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    Log10,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Log10("$var")
        result = compile_expression(op, context=context)
        assert result == {"$log10": "$var"}


def test_query(context, subtests: pytest.Subtests):
    op = Log10("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
