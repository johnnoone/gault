import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    SubStrCP,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SubStrCP("$input", "$index", "$count")
        result = compile_expression(op, context=context)
        assert result == {"$substrCP": ["$input", "$index", "$count"]}


def test_query(context, subtests: pytest.Subtests):
    op = SubStrCP("$input", "$index", "$count")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
