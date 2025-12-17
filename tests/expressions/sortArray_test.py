import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    SortArray,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SortArray("$input", "$sorter")
        result = compile_expression(op, context=context)
        assert result == {"$sortArray": {"input": "$input", "sortBy": "$sorter"}}


def test_query(context, subtests: pytest.Subtests):
    op = SortArray("$input", "$sorter")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
