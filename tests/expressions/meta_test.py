import pytest

from strata.expressions import Meta


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Meta("textScore")
        result = op.compile_expression(context=context)
        assert result == {"$meta": "textScore"}
