import math

import pytest

from strata.expressions import Cos


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Cos(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$cos": math.nan}

    with subtests.test():
        op = Cos(None)
        result = op.compile_expression(context=context)
        assert result == {"$cos": None}

    with subtests.test():
        op = Cos({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$cos": {"$divide": ["$side_b", "$hypotenuse"]}}
