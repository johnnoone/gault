import pytest

from gault.expressions import IndexOfBytes


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IndexOfBytes("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {"$indexOfBytes": ["$one", "$two"]}
