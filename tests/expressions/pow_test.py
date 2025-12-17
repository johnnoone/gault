import pytest
from strata.compilers import CompilationError
from strata.expressions import Pow, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Pow(1, 2)
        result = compile_expression(op, context=context)
        assert result == {"$pow": [1, 2]}


def test_query(context, subtests: pytest.Subtests):
    op = Pow(1, 2)
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
