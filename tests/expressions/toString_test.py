import pytest

from gault.expressions import ToString


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToString("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toString": "$one"}
