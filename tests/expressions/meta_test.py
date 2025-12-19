import pytest

from gault.expressions import Meta


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Meta("textScore")
        result = op.compile_expression(context=context)
        assert result == {"$meta": "textScore"}
