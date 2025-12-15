import pytest
from strata.expressions import (
    Atan2,
    CompilationError,
    compile_expression,
    compile_query,
)
import math


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Atan2(math.nan, "$side_a")
        result = compile_expression(op, context=context)
        assert result == {"$atan2": [math.nan, "$side_a"]}

    with subtests.test():
        op = Atan2(None, "$side_a")
        result = compile_expression(op, context=context)
        assert result == {"$atan2": [None, "$side_a"]}

    with subtests.test():
        op = Atan2({"$divide": ["$side_b", "$hypotenuse"]}, "$side_a")
        result = compile_expression(op, context=context)
        assert result == {
            "$atan2": [{"$divide": ["$side_b", "$hypotenuse"]}, "$side_a"]
        }


def test_query(context, subtests: pytest.Subtests):
    op = Atan2("$side_a", "$side_b")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
