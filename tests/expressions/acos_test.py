import math

import pytest

from strata.compilers import CompilationError
from strata.expressions import Acos, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Acos(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$acos": math.nan}

    with subtests.test():
        op = Acos(None)
        result = compile_expression(op, context=context)
        assert result == {"$acos": None}

    with subtests.test():
        op = Acos({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$acos": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Acos("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
