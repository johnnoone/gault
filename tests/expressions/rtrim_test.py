import pytest

from gault.expressions import Rtrim


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Rtrim("$var", chars="abc")
        result = op.compile_expression(context=context)
        assert result == {
            "$rtrim": {"input": "$var", "chars": "abc"},
        }
