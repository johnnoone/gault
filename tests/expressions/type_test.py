import pytest

from gault.expressions import Type


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Type("$one")
        result = op.compile_expression(context=context)
        assert result == {"$type": "$one"}
