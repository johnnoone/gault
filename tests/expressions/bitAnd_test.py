import pytest

from strata.expressions import BitAnd


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BitAnd("$a", "$b")
        result = op.compile_expression(context=context)
        assert result == {"$bitAnd": ["$a", "$b"]}

    with subtests.test():
        op = BitAnd("$a", 42)
        result = op.compile_expression(context=context)
        assert result == {"$bitAnd": ["$a", 42]}
