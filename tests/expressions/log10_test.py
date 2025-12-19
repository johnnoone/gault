import pytest

from gault.expressions import Log10


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Log10("$var")
        result = op.compile_expression(context=context)
        assert result == {"$log10": "$var"}
