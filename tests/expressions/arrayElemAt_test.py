import pytest

from gault.expressions import ArrayElemAt


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ArrayElemAt([1, 2, 3, "$a", "$b", "$c"], index=0)
        result = op.compile_expression(context=context)
        assert result == {"$arrayElemAt": [[1, 2, 3, "$a", "$b", "$c"], 0]}

    with subtests.test():
        op = ArrayElemAt("$responses", index=0)
        result = op.compile_expression(context=context)
        assert result == {"$arrayElemAt": ["$responses", 0]}
