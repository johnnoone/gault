import pytest
from strata.expressions import (
    CompilationError,
    UnsetField,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = UnsetField("$one", "$two")
        result = compile_expression(op, context=context)
        assert result == {
            "$unsetField": {
                "field": "$one",
                "input": "$two",
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = UnsetField("$one", "$two")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
