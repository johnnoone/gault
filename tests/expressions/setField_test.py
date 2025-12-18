import pytest

from strata.expressions import SetField


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetField("$input", "$field", "$value")
        result = op.compile_expression(context=context)
        assert result == {
            "$setField": {"field": "$field", "input": "$input", "value": "$value"}
        }
