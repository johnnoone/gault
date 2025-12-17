import pytest

from strata.compilers import CompilationError
from strata.expressions import Subtract, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Subtract("$input1", "$input2")
        result = compile_expression(op, context=context)
        assert result == {"$subtract": ["$input1", "$input2"]}


def test_query(context, subtests: pytest.Subtests):
    op = Subtract("$input1", "$input2")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
