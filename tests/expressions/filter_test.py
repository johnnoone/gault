import pytest

from strata.compilers import CompilationError
from strata.expressions import (Filter, IsNumber, Var, compile_expression,
                                compile_query)


def test_expression(context, subtests: pytest.Subtests):
    op = Filter(
        input=[1, "a", 2, None, 3.1, 4, "5"],
        var=Var("num"),
        cond=IsNumber(Var("num")),
    )
    result = compile_expression(op, context=context)
    assert result == {
        "$filter": {
            "input": [1, "a", 2, None, 3.1, 4, "5"],
            "as": "num",
            "cond": {"$isNumber": "$$num"},
        }
    }


def test_cond_is_callable(context, subtests: pytest.Subtests):
    op = Filter(
        input=[1, "a", 2, None, 3.1, 4, "5"],
        cond=lambda this, _: IsNumber(this),
    )
    result = compile_expression(op, context=context)
    assert result == {
        "$filter": {
            "input": [1, "a", 2, None, 3.1, 4, "5"],
            "cond": {"$isNumber": "$$this"},
        }
    }


def test_query(context, subtests: pytest.Subtests):
    op = Filter(
        input=[1, "a", 2, None, 3.1, 4, "5"],
        var=Var("num"),
        cond={"$isNumber": Var("num")},
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
