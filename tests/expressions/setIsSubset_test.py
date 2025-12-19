import pytest

from gault.expressions import SetIsSubset


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetIsSubset("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$setIsSubset": ["$one", "$two"]}
