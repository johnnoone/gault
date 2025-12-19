import pytest

from gault.expressions import ToDouble


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToDouble("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toDouble": "$one"}
