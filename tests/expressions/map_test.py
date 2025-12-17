import pytest

from strata.compilers import CompilationError
from strata.expressions import Map, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Map("$input", "$in", var="var")
        result = compile_expression(op, context=context)
        assert result == {
            "$map": {"input": "$input", "as": "var", "in": "$in"},
        }


def test_query(context, subtests: pytest.Subtests):
    op = Map("$input", "$in", var="var")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
