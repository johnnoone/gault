import pytest
from strata.expressions import (
    CompilationError,
    Trunc,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Trunc("$one", "$place")
        result = compile_expression(op, context=context)
        assert result == {"$trunc": ["$one", "$place"]}


def test_query(context, subtests: pytest.Subtests):
    op = Trunc("$one", "$place")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
