import pytest

from gault.expressions import Tan


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Tan("$one")
        result = op.compile_expression(context=context)
        assert result == {"$tan": "$one"}
