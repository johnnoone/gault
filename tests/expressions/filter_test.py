import pytest

from gault.expressions import Filter, IsNumber, Var


def test_expression(context, subtests: pytest.Subtests):
    op = Filter(
        input=[1, "a", 2, None, 3.1, 4, "5"],
        var=Var("num"),
        cond=IsNumber(Var("num")),
    )
    result = op.compile_expression(context=context)
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
    result = op.compile_expression(context=context)
    assert result == {
        "$filter": {
            "input": [1, "a", 2, None, 3.1, 4, "5"],
            "cond": {"$isNumber": "$$this"},
        }
    }
