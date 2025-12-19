import pytest

from gault.expressions import SetDifference


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetDifference("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$setDifference": ["$one", "$two"]}
