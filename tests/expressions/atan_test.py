import pytest
from strata.compilers import CompilationError
from strata.expressions import Atan, compile_expression, compile_query
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Atan(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$atan": math.nan}

    with subtests.test():
        op = Atan(None)
        result = compile_expression(op, context=context)
        assert result == {"$atan": None}

    with subtests.test():
        op = Atan({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$atan": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Atan("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
