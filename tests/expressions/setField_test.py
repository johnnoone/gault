import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    SetField,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SetField("$field", "$input", "$value")
        result = compile_expression(op, context=context)
        assert result == {
            "$setField": {"field": "$field", "input": "$input", "value": "$value"}
        }


def test_query(context, subtests: pytest.Subtests):
    op = SetField("$field", "$input", "$value")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
