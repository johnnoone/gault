import pytest
from strata.expressions import (
    CompilationError,
    ToDouble,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ToDouble("$one")
        result = compile_expression(op, context=context)
        assert result == {"$toDouble": "$one"}


def test_query(context, subtests: pytest.Subtests):
    op = ToDouble("$one")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
