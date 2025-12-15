import pytest
from strata.expressions import (
    CompilationError,
    Ltrim,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ltrim("$var", chars="abc")
        result = compile_expression(op, context=context)
        assert result == {
            "$ltrim": {"input": "$var", "chars": "abc"},
        }


def test_query(context, subtests: pytest.Subtests):
    op = Ltrim("$var", chars="abc")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
