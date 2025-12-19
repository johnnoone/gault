import pytest

from gault.expressions import Or


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Or([1, 2, 3, "$a", "$b", "$c"])
        result = op.compile_expression(context=context)
        assert result == {"$or": [1, 2, 3, "$a", "$b", "$c"]}

    with subtests.test():
        op = Or(1, 2, 3, "$a", "$b", "$c")
        result = op.compile_expression(context=context)
        assert result == {"$or": [1, 2, 3, "$a", "$b", "$c"]}


def test_query(context, subtests: pytest.Subtests):
    op = Or([1, 2, 3, "$a", "$b", "$c"])
    result = op.compile_expression(context=context)
    assert result == {"$or": [1, 2, 3, "$a", "$b", "$c"]}
