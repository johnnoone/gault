import pytest

from strata.expressions import Ltrim


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ltrim("$var", chars="abc")
        result = op.compile_expression(context=context)
        assert result == {
            "$ltrim": {"input": "$var", "chars": "abc"},
        }
