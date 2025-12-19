import pytest

from gault.expressions import ToDecimal


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToDecimal("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toDecimal": "$one"}
