import math

import pytest

from gault.expressions import Cosh


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Cosh(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$cosh": math.nan}

    with subtests.test():
        op = Cosh(None)
        result = op.compile_expression(context=context)
        assert result == {"$cosh": None}

    with subtests.test():
        op = Cosh({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$cosh": {"$divide": ["$side_b", "$hypotenuse"]}}
