import pytest

from strata.compilers import CompilationError
from strata.expressions import Let, Literal, Var, compile_expression, compile_query


def test_expression1(context, subtests: pytest.Subtests):
    op = Let(
        {"low": 1, "high": Var("low")},
        into={"$gt": ["$$low", "$$high"]},
    )
    result = compile_expression(op, context=context)
    assert result == {
        "$let": {
            "vars": {"low": 1, "high": "$$low"},
            "in": {"$gt": ["$$low", "$$high"]},
        }
    }


def test_expression2(context, subtests: pytest.Subtests):
    op = Let(
        {Var("low"): 1, "high": Var("low")},
        into={"$gt": ["$$low", "$$high"]},
    )
    result = compile_expression(op, context=context)
    assert result == {
        "$let": {
            "vars": {"low": 1, "high": "$$low"},
            "in": {"$gt": ["$$low", "$$high"]},
        }
    }


def test_expression3(context, subtests: pytest.Subtests):
    op = Let(
        Literal(1).alias("low"),
        Var("low").alias("high"),
        into={"$gt": ["$$low", "$$high"]},
    )
    result = compile_expression(op, context=context)
    assert result == {
        "$let": {
            "vars": {"low": {"$literal": 1}, "high": "$$low"},
            "in": {"$gt": ["$$low", "$$high"]},
        }
    }


def test_query(context, subtests: pytest.Subtests):
    op = Let(
        {Var("low"): 1, "high": Var("low")},
        into={"$gt": ["$$low", "$$high"]},
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
