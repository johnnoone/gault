import pytest
from strata.compilers import CompilationError
from strata.expressions import Log, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Log("$var", base=2)
        result = compile_expression(op, context=context)
        assert result == {"$log": ["$var", 2]}


def test_query(context, subtests: pytest.Subtests):
    op = Log("$var", base=2)
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
