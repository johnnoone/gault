import pytest

from gault.expressions import Concat


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Concat("$item", " - ", "$description")
        result = op.compile_expression(context=context)
        assert result == {"$concat": ["$item", " - ", "$description"]}
