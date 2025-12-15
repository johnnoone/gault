import pytest
from strata.expressions import Or, CompilationError, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Or([1, 2, 3, "$a", "$b", "$c"])
        result = compile_expression(op, context=context)
        assert result == {"$or": [1, 2, 3, "$a", "$b", "$c"]}

    with subtests.test():
        op = Or(1, 2, 3, "$a", "$b", "$c")
        result = compile_expression(op, context=context)
        assert result == {"$or": [1, 2, 3, "$a", "$b", "$c"]}


def test_query(context, subtests: pytest.Subtests):
    op = Or([1, 2, 3, "$a", "$b", "$c"])
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target == 1
