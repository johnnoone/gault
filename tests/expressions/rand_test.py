import pytest

from gault.expressions import Rand


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Rand()
        result = op.compile_expression(context=context)
        assert result == {"$rand": {}}
