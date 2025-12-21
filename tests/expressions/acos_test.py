import math

import pytest


from gault.expressions import Acos


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Acos(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$acos": math.nan}

    with subtests.test():
        op = Acos("$other")
        result = op.compile_expression(context=context)
        assert result == {"$acos": "$other"}

    with subtests.test():
        op = Acos({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$acos": {"$divide": ["$side_b", "$hypotenuse"]}}
