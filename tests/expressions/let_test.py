import pytest

from gault.expressions import Let, Literal, Var


def test_expression1(context, subtests: pytest.Subtests):
    op = Let(
        {"low": 1, "high": Var("low")},
        into={"$gt": ["$$low", "$$high"]},
    )
    result = op.compile_expression(context=context)
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
    result = op.compile_expression(context=context)
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
    result = op.compile_expression(context=context)
    assert result == {
        "$let": {
            "vars": {"low": {"$literal": 1}, "high": "$$low"},
            "in": {"$gt": ["$$low", "$$high"]},
        }
    }
