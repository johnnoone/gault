import pytest
from strata.expressions import (
    Acosh,
    CompilationError,
    compile_expression,
    compile_query,
)
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Acosh(math.nan)
        result = compile_expression(op, context=context)
        assert result == {"$acosh": math.nan}

    with subtests.test():
        op = Acosh(None)
        result = compile_expression(op, context=context)
        assert result == {"$acosh": None}

    with subtests.test():
        op = Acosh({"$divide": ["$side_b", "$hypotenuse"]})
        result = compile_expression(op, context=context)
        assert result == {"$acosh": {"$divide": ["$side_b", "$hypotenuse"]}}


def test_query(context, subtests: pytest.Subtests):
    op = Acosh("$side")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
