import pytest

from strata.expressions import SetUnion


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetUnion("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$setUnion": ["$one", "$two"]}
