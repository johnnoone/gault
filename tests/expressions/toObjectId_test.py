import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    ToObjectId,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToObjectId("$one")
        result = compile_expression(op, context=context)
        assert result == {"$toObjectId": "$one"}


def test_query(context, subtests: pytest.Subtests):
    op = ToObjectId("$one")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
