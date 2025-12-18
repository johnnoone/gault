import pytest

from strata.expressions import ToHashedIndexKey


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToHashedIndexKey("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toHashedIndexKey": "$one"}
