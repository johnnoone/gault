import pytest
from strata.compilers import CompilationError
from strata.expressions import Add, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Add([1, 2, 3, "$a", "$b", "$c"])
        result = compile_expression(op, context=context)
        assert result == {"$add": [1, 2, 3, "$a", "$b", "$c"]}

    with subtests.test():
        op = Add(1, 2, 3, "$a", "$b", "$c")
        result = compile_expression(op, context=context)
        assert result == {"$add": [1, 2, 3, "$a", "$b", "$c"]}


def test_query(context, subtests: pytest.Subtests):
    op = Add([1, 2, 3, "$a", "$b", "$c"])
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
