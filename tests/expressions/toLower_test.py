import pytest

from strata.expressions import ToLower


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToLower("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toLower": "$one"}
