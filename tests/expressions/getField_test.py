import pytest

from strata.expressions import GetField


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = GetField(
            field={"$literal": "$small"},
            input="$quantity",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$getField": {
                "field": {"$literal": "$small"},
                "input": "$quantity",
            }
        }
