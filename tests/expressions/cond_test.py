import pytest
from strata.expressions import Cond, compile_expression, compile_query
from strata.compilers import CompilationError


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Cond(
            when={"$gte": ["$qty", 250]},
            then=30,
            otherwise=20,
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$cond": {
                "if": {"$gte": ["$qty", 250]},
                "then": 30,
                "else": 20,
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = Cond(
        when={"$gte": ["$qty", 250]},
        then=30,
        otherwise=20,
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
