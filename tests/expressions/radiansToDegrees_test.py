import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    RadiansToDegrees,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = RadiansToDegrees(1)
        result = compile_expression(op, context=context)
        assert result == {"$radiansToDegrees": 1}


def test_query(context, subtests: pytest.Subtests):
    op = RadiansToDegrees(1)
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
