import pytest

from gault.expressions import SubStrCP


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SubStrCP("$input", "$index", "$count")
        result = op.compile_expression(context=context)
        assert result == {"$substrCP": ["$input", "$index", "$count"]}
