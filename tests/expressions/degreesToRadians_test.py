import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    DegreesToRadians,
    compile_expression,
    compile_query,
)
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DegreesToRadians(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$degreesToRadians": math.nan}

    with subtests.test():
        op = DegreesToRadians(None)
        result = compile_expression(op, context=context)
        assert result == {"$degreesToRadians": None}

    with subtests.test():
        op = DegreesToRadians({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$degreesToRadians": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = DegreesToRadians("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
