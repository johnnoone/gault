import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    ReplaceAll,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ReplaceAll(
            input="$category",
            find="cafe",
            replacement="croissant",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$replaceAll": {
                "input": "$category",
                "find": "cafe",
                "replacement": "croissant",
            },
        }


def test_query(context, subtests: pytest.Subtests):
    op = ReplaceAll(
        input="$category",
        find="cafe",
        replacement="croissant",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
