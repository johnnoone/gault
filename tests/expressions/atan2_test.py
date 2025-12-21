import math

import pytest

from gault.expressions import Atan2


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Atan2(math.nan, "$side_a")
        result = op.compile_expression(context=context)
        assert result == {"$atan2": [math.nan, "$side_a"]}

    with subtests.test():
        op = Atan2(21, "$side_a")
        result = op.compile_expression(context=context)
        assert result == {"$atan2": [21, "$side_a"]}

    with subtests.test():
        op = Atan2({"$divide": ["$side_b", "$hypotenuse"]}, "$side_a")
        result = op.compile_expression(context=context)
        assert result == {
            "$atan2": [{"$divide": ["$side_b", "$hypotenuse"]}, "$side_a"]
        }
