import pytest

from gault.expressions import Cond


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
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
