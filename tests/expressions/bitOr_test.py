import pytest

from gault.expressions import BitOr


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BitOr("$a", "$b")
        result = op.compile_expression(context=context)
        assert result == {"$bitOr": ["$a", "$b"]}

    with subtests.test():
        op = BitOr("$a", 42)
        result = op.compile_expression(context=context)
        assert result == {"$bitOr": ["$a", 42]}
