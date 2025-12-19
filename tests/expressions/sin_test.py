import pytest

from gault.expressions import Sin


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Sin("$one")
        result = op.compile_expression(context=context)
        assert result == {"$sin": "$one"}
