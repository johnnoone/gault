import pytest
from strata.expressions import Ceil, CompilationError, compile_expression, compile_query
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ceil(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$ceil": math.nan}

    with subtests.test():
        op = Ceil(None)
        result = compile_expression(op, context=context)
        assert result == {"$ceil": None}

    with subtests.test():
        op = Ceil({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$ceil": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Ceil("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
