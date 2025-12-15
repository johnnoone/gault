import pytest
from strata.expressions import (
    CompilationError,
    StrCaseCmp,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = StrCaseCmp("$input1", "$input2")
        result = compile_expression(op, context=context)
        assert result == {"$strcasecmp": ["$input1", "$input2"]}


def test_query(context, subtests: pytest.Subtests):
    op = StrCaseCmp("$input1", "$input2")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
