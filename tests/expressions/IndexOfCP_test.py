import pytest

from gault.expressions import IndexOfCP


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IndexOfCP("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$indexOfCP": ["$one", "$two"]}
