import pytest

from strata.expressions import ObjectToArray


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ObjectToArray("field")
        result = op.compile_expression(context=context)
        assert result == {"$objectToArray": "field"}
