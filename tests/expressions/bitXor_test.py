import pytest

from gault.expressions import BitXor


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BitXor("$a", "$b")
        result = op.compile_expression(context=context)
        assert result == {"$bitXor": ["$a", "$b"]}

    with subtests.test():
        op = BitXor("$a", 42)
        result = op.compile_expression(context=context)
        assert result == {"$bitXor": ["$a", 42]}
