import pytest

from strata.expressions import BitNot


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BitNot("$a")
        result = op.compile_expression(context=context)
        assert result == {"$bitNot": "$a"}
