import pytest
from strata.compilers import CompilationError
from strata.expressions import Asin, compile_expression, compile_query
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Asin(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$asin": math.nan}

    with subtests.test():
        op = Asin(None)
        result = compile_expression(op, context=context)
        assert result == {"$asin": None}

    with subtests.test():
        op = Asin({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$asin": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Asin("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
