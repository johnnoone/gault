import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    Rtrim,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Rtrim("$var", chars="abc")
        result = compile_expression(op, context=context)
        assert result == {
            "$rtrim": {"input": "$var", "chars": "abc"},
        }


def test_query(context, subtests: pytest.Subtests):
    op = Rtrim("$var", chars="abc")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
