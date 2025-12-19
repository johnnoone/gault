import pytest

from gault.expressions import IndexOfArray


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IndexOfArray("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$indexOfArray": ["$one", "$two"]}
