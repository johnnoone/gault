import pytest

from gault.expressions import RadiansToDegrees


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = RadiansToDegrees(1)
        result = op.compile_expression(context=context)
        assert result == {"$radiansToDegrees": 1}
