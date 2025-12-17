import pytest

from strata.compilers import CompilationError
from strata.expressions import BitOr, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BitOr("$a", "$b")
        result = compile_expression(op, context=context)
        assert result == {"$bitOr": ["$a", "$b"]}

    with subtests.test():
        op = BitOr("$a", 42)
        result = compile_expression(op, context=context)
        assert result == {"$bitOr": ["$a", 42]}


def test_query(context, subtests: pytest.Subtests):
    op = BitOr("$a", "$b")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
