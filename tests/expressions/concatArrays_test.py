import pytest

from gault.expressions import ConcatArrays


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ConcatArrays(["hello", " "], ["world"])
        result = op.compile_expression(context=context)
        assert result == {"$concatArrays": [["hello", " "], ["world"]]}
