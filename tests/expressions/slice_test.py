import pytest

from strata.compilers import CompilationError
from strata.expressions import Slice, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Slice("$input", n="$n", position="$pos")
        result = compile_expression(op, context=context)
        assert result == {"$slice": ["$input", "$pos", "$n"]}

    with subtests.test():
        op = Slice("$input", n="$n")
        result = compile_expression(op, context=context)
        assert result == {"$slice": ["$input", "$n"]}


def test_query(context, subtests: pytest.Subtests):
    op = Slice("$input", n="$n", position="$pos")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
