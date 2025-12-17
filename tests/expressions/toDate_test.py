import pytest

from strata.compilers import CompilationError
from strata.expressions import ToDate, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToDate("$one")
        result = compile_expression(op, context=context)
        assert result == {"$toDate": "$one"}


def test_query(context, subtests: pytest.Subtests):
    op = ToDate("$one")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
