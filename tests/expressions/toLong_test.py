import pytest
from strata.expressions import (
    CompilationError,
    ToLong,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToLong("$one")
        result = compile_expression(op, context=context)
        assert result == {"$toLong": "$one"}


def test_query(context, subtests: pytest.Subtests):
    op = ToLong("$one")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
