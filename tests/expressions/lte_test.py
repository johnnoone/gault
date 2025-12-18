import pytest

from strata.expressions import Lte


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Lte("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$lte": ["field", "value"]}

    with subtests.test():
        op = Lte("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$lte": ["field", "$value"]}
