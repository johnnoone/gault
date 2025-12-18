import pytest

from strata.expressions import And


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = And([1, 2, 3, "$a", "$b", "$c"])
        result = op.compile_expression(context=context)
        assert result == {"$and": [1, 2, 3, "$a", "$b", "$c"]}

    with subtests.test():
        op = And(1, 2, 3, "$a", "$b", "$c")
        result = op.compile_expression(context=context)
        assert result == {"$and": [1, 2, 3, "$a", "$b", "$c"]}
