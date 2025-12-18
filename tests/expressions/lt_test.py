import pytest

from strata.expressions import Lt


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Lt("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$lt": ["field", "value"]}

    with subtests.test():
        op = Lt("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$lt": ["field", "$value"]}
