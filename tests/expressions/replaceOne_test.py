import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    ReplaceOne,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ReplaceOne(
            input="$category",
            find="cafe",
            replacement="croissant",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$replaceOne": {
                "input": "$category",
                "find": "cafe",
                "replacement": "croissant",
            },
        }


def test_query(context, subtests: pytest.Subtests):
    op = ReplaceOne(
        input="$category",
        find="cafe",
        replacement="croissant",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
