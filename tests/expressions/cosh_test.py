import math

import pytest

from strata.compilers import CompilationError
from strata.expressions import Cosh, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Cosh(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$cosh": math.nan}

    with subtests.test():
        op = Cosh(None)
        result = compile_expression(op, context=context)
        assert result == {"$cosh": None}

    with subtests.test():
        op = Cosh({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$cosh": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Cosh("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
