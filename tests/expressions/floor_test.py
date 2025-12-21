import math

import pytest

from gault.expressions import Floor


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Floor(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$floor": math.nan}

    with subtests.test():
        op = Floor(21)
        result = op.compile_expression(context=context)
        assert result == {"$floor": 21}

    with subtests.test():
        op = Floor({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$floor": {"$divide": ["$side_b", "$hypotenuse"]}}
