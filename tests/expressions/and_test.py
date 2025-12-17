import pytest
from strata.expressions import And, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = And([1, 2, 3, "$a", "$b", "$c"])
        result = compile_expression(op, context=context)
        assert result == {"$and": [1, 2, 3, "$a", "$b", "$c"]}

    with subtests.test():
        op = And(1, 2, 3, "$a", "$b", "$c")
        result = compile_expression(op, context=context)
        assert result == {"$and": [1, 2, 3, "$a", "$b", "$c"]}


def test_query(context, subtests: pytest.Subtests):
    op = And([1, 2, 3, "$a", "$b", "$c"])
    result = compile_query(op, context=context)
    assert result == {"$and": [1, 2, 3, "$a", "$b", "$c"]}
