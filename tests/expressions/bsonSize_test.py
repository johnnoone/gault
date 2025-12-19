import pytest

from gault.expressions import BsonSize


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = BsonSize("$a")
        result = op.compile_expression(context=context)
        assert result == {"$bsonSize": "$a"}
