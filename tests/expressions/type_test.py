import pytest
from strata.expressions import (
    CompilationError,
    Type,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Type("$one")
        result = compile_expression(op, context=context)
        assert result == {"$type": "$one"}


def test_query(context, subtests: pytest.Subtests):
    op = Type("$one")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
