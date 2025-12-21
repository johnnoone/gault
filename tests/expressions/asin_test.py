import math

import pytest

from gault.expressions import Asin


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Asin(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$asin": math.nan}

    with subtests.test():
        op = Asin(31)
        result = op.compile_expression(context=context)
        assert result == {"$asin": 31}

    with subtests.test():
        op = Asin({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$asin": {"$divide": ["$side_b", "$hypotenuse"]}}
