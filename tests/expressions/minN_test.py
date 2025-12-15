import pytest
from strata.expressions import (
    CompilationError,
    MinN,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = MinN("$input", n=2)
        result = compile_expression(op, context=context)
        assert result == {
            "$minN": {"input": "$input", "n": 2},
        }


def test_query(context, subtests: pytest.Subtests):
    op = MinN("$input", n=2)
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
