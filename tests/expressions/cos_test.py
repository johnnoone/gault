import math

import pytest

from strata.compilers import CompilationError
from strata.expressions import Cos, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Cos(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$cos": math.nan}

    with subtests.test():
        op = Cos(None)
        result = compile_expression(op, context=context)
        assert result == {"$cos": None}

    with subtests.test():
        op = Cos({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$cos": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Cos("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
