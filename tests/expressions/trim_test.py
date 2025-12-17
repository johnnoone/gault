import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    Trim,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Trim("$one", chars="$chars")
        result = compile_expression(op, context=context)
        assert result == {"$trim": {"chars": "$chars", "input": "$one"}}


def test_query(context, subtests: pytest.Subtests):
    op = Trim("$one", chars="$chars")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
