import pytest

from gault.expressions import Not


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Not("field")
        result = op.compile_expression(context=context)
        assert result == {"$not": ["field"]}
