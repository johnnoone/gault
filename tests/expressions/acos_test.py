import math

import pytest


from strata.expressions import Acos


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Acos(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$acos": math.nan}

    with subtests.test():
        op = Acos(None)
        result = op.compile_expression(context=context)
        assert result == {"$acos": None}

    with subtests.test():
        op = Acos({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$acos": {"$divide": ["$side_b", "$hypotenuse"]}}
