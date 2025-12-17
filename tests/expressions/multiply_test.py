import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    Multiply,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Multiply("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$multiply": ["field", "value"]}

    with subtests.test():
        op = Multiply("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$multiply": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    op = Multiply("field", "value")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
