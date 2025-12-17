import pytest

from strata.compilers import CompilationError
from strata.expressions import Concat, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Concat("$item", " - ", "$description")
        result = compile_expression(op, context=context)
        assert result == {"$concat": ["$item", " - ", "$description"]}


def test_query(context, subtests: pytest.Subtests):
    op = Concat("$item", " - ", "$description")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
