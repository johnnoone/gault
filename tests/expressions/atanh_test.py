import pytest
from strata.compilers import CompilationError
from strata.expressions import (
    Atanh,
    compile_expression,
    compile_query,
)
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Atanh(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$atanh": math.nan}

    with subtests.test():
        op = Atanh(None)
        result = compile_expression(op, context=context)
        assert result == {"$atanh": None}

    with subtests.test():
        op = Atanh({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$atanh": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Atanh("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
