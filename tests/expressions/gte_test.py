import pytest

from gault.expressions import Gte


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Gte("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$gte": ["field", "value"]}

    with subtests.test():
        op = Gte("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$gte": ["field", "$value"]}
