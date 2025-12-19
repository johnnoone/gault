import pytest

from gault.expressions import Split


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Split("$input", "$delim")
        result = op.compile_expression(context=context)
        assert result == {"$split": ["$input", "$delim"]}
