import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    IndexOfCP,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IndexOfCP("$one", "$two")
        result = compile_expression(op, context=context)
        assert result == {"$indexOfCP": ["$one", "$two"]}


def test_query(context, subtests: pytest.Subtests):
    op = IndexOfCP("$one", "$two")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
