import pytest

from strata.compilers import CompilationError
from strata.expressions import SetIsSubset, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetIsSubset("$one", "$two")
        result = compile_expression(op, context=context)
        assert result == {"$setIsSubset": ["$one", "$two"]}


def test_query(context, subtests: pytest.Subtests):
    op = SetIsSubset("$one", "$two")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
