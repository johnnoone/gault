import pytest

from strata.expressions import SetIntersection


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetIntersection("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$setIntersection": ["$one", "$two"]}
