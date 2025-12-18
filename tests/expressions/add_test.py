import pytest

from strata.expressions import Add


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Add([1, 2, 3, "$a", "$b", "$c"])
        result = op.compile_expression(context=context)
        assert result == {"$add": [1, 2, 3, "$a", "$b", "$c"]}

    with subtests.test():
        op = Add(1, 2, 3, "$a", "$b", "$c")
        result = op.compile_expression(context=context)
        assert result == {"$add": [1, 2, 3, "$a", "$b", "$c"]}
