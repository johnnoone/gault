import pytest

from gault.expressions import IsNumber


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IsNumber("$one")
        result = op.compile_expression(context=context)
        assert result == {"$isNumber": "$one"}
