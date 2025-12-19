import pytest

from gault.expressions import ToUpper


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToUpper("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toUpper": "$one"}
