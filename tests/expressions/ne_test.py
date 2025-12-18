import pytest

from strata.expressions import Ne


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ne("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$ne": ["field", "value"]}

    with subtests.test():
        op = Ne("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$ne": ["field", "$value"]}
