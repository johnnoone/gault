import pytest

from strata.expressions import Map


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Map("$input", "$in", var="var")
        result = op.compile_expression(context=context)
        assert result == {
            "$map": {"input": "$input", "as": "var", "in": "$in"},
        }
