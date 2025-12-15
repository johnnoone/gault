import pytest
from strata.expressions import (
    Filter,
    CompilationError,
    Var,
    compile_expression,
    compile_query,
    IsNumber,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Filter(
            input=[1, "a", 2, None, 3.1, 4, "5"],
            into=Var("num"),
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


def test_query(context, subtests: pytest.Subtests):
    op = Filter(
        input=[1, "a", 2, None, 3.1, 4, "5"],
        into=Var("num"),
        cond={"$isNumber": Var("num")},
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
