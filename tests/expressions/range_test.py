import pytest

from gault.expressions import Range


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Range(0, 1, step=3)
        result = op.compile_expression(context=context)
        assert result == {"$range": [0, 1, 3]}
