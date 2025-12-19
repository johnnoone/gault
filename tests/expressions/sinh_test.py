import pytest

from gault.expressions import Sinh


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Sinh("$one")
        result = op.compile_expression(context=context)
        assert result == {"$sinh": "$one"}
