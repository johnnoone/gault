import pytest
from strata.expressions import (
    CompilationError,
    SetIntersection,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetIntersection("$one", "$two")
        result = compile_expression(op, context=context)
        assert result == {"$setIntersection": ["$one", "$two"]}


def test_query(context, subtests: pytest.Subtests):
    op = SetIntersection("$one", "$two")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
