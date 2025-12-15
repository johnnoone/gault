import pytest
from strata.expressions import Abs, compile_expression, compile_query, CompilationError


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Abs("$field")
        result = compile_expression(op, context=context)
        assert result == {"$abs": "$field"}

    with subtests.test():
        op = Abs(-1)
        result = compile_expression(op, context=context)
        assert result == {"$abs": -1}

    with subtests.test():
        op = Abs(None)
        result = compile_expression(op, context=context)
        assert result == {"$abs": None}

    with subtests.test():
        op = Abs(12)
        result = compile_expression(op, context=context)
        assert result == {"$abs": 12}

    with subtests.test():
        op = Abs({"$subtract": ["$startTemp", "$endTemp"]})
        result = compile_expression(op, context=context)
        assert result == {"$abs": {"$subtract": ["$startTemp", "$endTemp"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Abs("$field")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
