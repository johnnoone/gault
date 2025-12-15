import pytest
from strata.expressions import (
    CompilationError,
    Reduce,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Reduce(
            input=["a", "b", "c"],
            initial_value="",
            into={"$concat": ["$$value", "$$this"]},
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$reduce": {
                "input": ["a", "b", "c"],
                "initialValue": "",
                "in": {"$concat": ["$$value", "$$this"]},
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = Reduce(
        input=["a", "b", "c"],
        initial_value="",
        into={"$concat": ["$$value", "$$this"]},
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
