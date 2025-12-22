import pytest

from gault.expressions import Cond
from gault import Field, Var


def test_when_raw_expression(context, subtests: pytest.Subtests):
    op = Cond(
        when={"$gte": ["$qty", 250]},
        then=30,
        otherwise=20,
    )
    result = op.compile_expression(context=context)
    assert result == {
        "$cond": {
            "if": {"$gte": ["$qty", 250]},
            "then": 30,
            "else": 20,
        }
    }


def test_when_predicate(context, subtests: pytest.Subtests):
    op = Cond(
        when=Field("some").eq(42),
        then=30,
        otherwise=20,
    )
    result = op.compile_expression(context=context)
    assert result == {
        "$cond": {
            "if": {"$eq": ["$some", 42]},
            "then": 30,
            "else": 20,
        }
    }


def test_when_expression(context, subtests: pytest.Subtests):
    op = Cond(
        when=Var("some").eq(42),
        then=30,
        otherwise=20,
    )
    result = op.compile_expression(context=context)
    assert result == {
        "$cond": {
            "if": {"$eq": ["$$some", 42]},
            "then": 30,
            "else": 20,
        }
    }
