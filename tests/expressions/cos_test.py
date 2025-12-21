import math

import pytest

from gault.expressions import Cos


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Cos(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$cos": math.nan}

    with subtests.test():
        op = Cos(21)
        result = op.compile_expression(context=context)
        assert result == {"$cos": 21}

    with subtests.test():
        op = Cos({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$cos": {"$divide": ["$side_b", "$hypotenuse"]}}
