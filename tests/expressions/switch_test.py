import pytest

from strata.expressions import Switch


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Switch([("$input1", "$input2")], default="$input3")
        result = op.compile_expression(context=context)
        assert result == {
            "$switch": {
                "branches": [{"case": "$input1", "then": "$input2"}],
                "default": "$input3",
            }
        }
