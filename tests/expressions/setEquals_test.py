import pytest

from gault.expressions import SetEquals


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetEquals("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$setEquals": ["$one", "$two"]}
