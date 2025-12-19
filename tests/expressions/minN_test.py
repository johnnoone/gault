import pytest

from gault.expressions import MinN


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = MinN("$input", n=2)
        result = op.compile_expression(context=context)
        assert result == {
            "$minN": {"input": "$input", "n": 2},
        }
