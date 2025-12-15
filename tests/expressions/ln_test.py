import pytest
from strata.expressions import Ln, CompilationError, compile_expression, compile_query
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ln(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$ln": math.nan}

    with subtests.test():
        op = Ln(None)
        result = compile_expression(op, context=context)
        assert result == {"$ln": None}

    with subtests.test():
        op = Ln({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$ln": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Ln("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
