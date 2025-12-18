import pytest

from strata.expressions import Reduce


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Reduce(
            input=["a", "b", "c"],
            initial_value="",
            into={"$concat": ["$$value", "$$this"]},
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$reduce": {
                "input": ["a", "b", "c"],
                "initialValue": "",
                "in": {"$concat": ["$$value", "$$this"]},
            }
        }
