import pytest

from strata.compilers import CompilationError
from strata.expressions import IfNull, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IfNull("$one", "$two", "$three")
        result = compile_expression(op, context=context)
        assert result == {"$ifNull": ["$one", "$two", "$three"]}

    with subtests.test():
        op = IfNull(["$one", "$two", "$three"])
        result = compile_expression(op, context=context)
        assert result == {"$ifNull": ["$one", "$two", "$three"]}


def test_query(context, subtests: pytest.Subtests):
    op = IfNull("$one", "$two", "$three")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
