import math

import pytest

from strata.compilers import CompilationError
from strata.expressions import Asinh, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Asinh(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$asinh": math.nan}

    with subtests.test():
        op = Asinh(None)
        result = compile_expression(op, context=context)
        assert result == {"$asinh": None}

    with subtests.test():
        op = Asinh({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$asinh": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Asinh("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
