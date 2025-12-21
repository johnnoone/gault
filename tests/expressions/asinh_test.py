import math

import pytest

from gault.expressions import Asinh


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Asinh(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$asinh": math.nan}

    with subtests.test():
        op = Asinh(21)
        result = op.compile_expression(context=context)
        assert result == {"$asinh": 21}

    with subtests.test():
        op = Asinh({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$asinh": {"$divide": ["$side_b", "$hypotenuse"]}}
