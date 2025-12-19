import pytest

from gault.expressions import ToObjectId


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToObjectId("$one")
        result = op.compile_expression(context=context)
        assert result == {"$toObjectId": "$one"}
