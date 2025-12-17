import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    AnyElementsTrue,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = AnyElementsTrue([1, 2, 3, "$a", "$b", "$c"])
        result = compile_expression(op, context=context)
        assert result == {"$anyElementsTrue": [[1, 2, 3, "$a", "$b", "$c"]]}

    with subtests.test():
        op = AnyElementsTrue("$responses")
        result = compile_expression(op, context=context)
        assert result == {"$anyElementsTrue": ["$responses"]}


def test_query(context, subtests: pytest.Subtests):
    op = AnyElementsTrue([1, 2, 3, "$a", "$b", "$c"])
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
