import pytest

from strata.compilers import CompilationError
from strata.expressions import ArrayElemAt, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ArrayElemAt([1, 2, 3, "$a", "$b", "$c"], index=0)
        result = compile_expression(op, context=context)
        assert result == {"$arrayElemAt": [[1, 2, 3, "$a", "$b", "$c"], 0]}

    with subtests.test():
        op = ArrayElemAt("$responses", index=0)
        result = compile_expression(op, context=context)
        assert result == {"$arrayElemAt": ["$responses", 0]}


def test_query(context, subtests: pytest.Subtests):
    op = ArrayElemAt([1, 2, 3, "$a", "$b", "$c"], index=0)
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
