import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    Round,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Round("$var")
        result = compile_expression(op, context=context)
        assert result == {
            "$round": ["$var", 0],
        }


def test_query(context, subtests: pytest.Subtests):
    op = Round("$var")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
