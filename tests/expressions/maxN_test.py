import pytest

from strata.expressions import MaxN


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = MaxN("$input", n=2)
        result = op.compile_expression(context=context)
        assert result == {
            "$maxN": {"input": "$input", "n": 2},
        }
