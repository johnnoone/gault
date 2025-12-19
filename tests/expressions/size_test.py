import pytest

from gault.expressions import Size


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Size("$one")
        result = op.compile_expression(context=context)
        assert result == {"$size": "$one"}
