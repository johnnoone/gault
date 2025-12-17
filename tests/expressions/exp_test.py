import math

import pytest

from strata.compilers import CompilationError
from strata.expressions import Exp, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Exp(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$exp": math.nan}

    with subtests.test():
        op = Exp(None)
        result = compile_expression(op, context=context)
        assert result == {"$exp": None}

    with subtests.test():
        op = Exp({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$exp": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Exp("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
