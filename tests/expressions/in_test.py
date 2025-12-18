import pytest

from strata.expressions import In


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = In("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$in": ["$one", "$two"]}
