import pytest

from gault.expressions import TsIncrement


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = TsIncrement("$one")
        result = op.compile_expression(context=context)
        assert result == {"$tsIncrement": "$one"}
