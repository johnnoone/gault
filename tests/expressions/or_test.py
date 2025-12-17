import pytest
from strata.expressions import Or, compile_expression


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
    result = compile_expression(op, context=context)
    assert result == {"$or": [1, 2, 3, "$a", "$b", "$c"]}
