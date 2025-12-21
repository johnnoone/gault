import math

import pytest

from gault.expressions import Atan


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Atan(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$atan": math.nan}

    with subtests.test():
        op = Atan(21)
        result = op.compile_expression(context=context)
        assert result == {"$atan": 21}

    with subtests.test():
        op = Atan({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$atan": {"$divide": ["$side_b", "$hypotenuse"]}}
