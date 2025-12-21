import math

import pytest

from gault.expressions import DegreesToRadians


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = DegreesToRadians(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$degreesToRadians": math.nan}

    with subtests.test():
        op = DegreesToRadians(21)
        result = op.compile_expression(context=context)
        assert result == {"$degreesToRadians": 21}

    with subtests.test():
        op = DegreesToRadians({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$degreesToRadians": {"$divide": ["$side_b", "$hypotenuse"]}}
