import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    Let,
    compile_expression,
    compile_query,
    Var,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Let(
            variables={Var("low"): 1, "high": Var("low")},
            into={"$gt": ["$$low", "$$high"]},
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$let": {
                "vars": {"low": 1, "high": "$$low"},
                "in": {"$gt": ["$$low", "$$high"]},
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = Let(
        variables={Var("low"): 1, "high": Var("low")},
        into={"$gt": ["$$low", "$$high"]},
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
