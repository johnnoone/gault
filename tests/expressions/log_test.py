import pytest

from gault.expressions import Log


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Log("$var", base=2)
        result = op.compile_expression(context=context)
        assert result == {"$log": ["$var", 2]}
