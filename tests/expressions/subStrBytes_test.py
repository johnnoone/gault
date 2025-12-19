import pytest

from gault.expressions import SubStrBytes


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SubStrBytes("$input1", "$index", "$count")
        result = op.compile_expression(context=context)
        assert result == {
            "$substrBytes": ["$input1", "$index", "$count"],
        }
