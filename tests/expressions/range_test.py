import pytest

from strata.compilers import CompilationError
from strata.expressions import Range, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Range(0, 1, step=3)
        result = compile_expression(op, context=context)
        assert result == {"$range": [0, 1, 3]}


def test_query(context, subtests: pytest.Subtests):
    op = Range(0, 1, step=3)
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
