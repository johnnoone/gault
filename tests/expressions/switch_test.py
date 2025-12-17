import pytest

from strata.compilers import CompilationError
from strata.expressions import Switch, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Switch([("$input1", "$input2")], default="$input3")
        result = compile_expression(op, context=context)
        assert result == {
            "$switch": {
                "branches": [{"case": "$input1", "then": "$input2"}],
                "default": "$input3",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = Switch([("$input1", "$input2")], default="$input3")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
