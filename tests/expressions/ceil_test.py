import math

import pytest

from gault.expressions import Ceil


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ceil(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$ceil": math.nan}

    with subtests.test():
        op = Ceil(21)
        result = op.compile_expression(context=context)
        assert result == {"$ceil": 21}

    with subtests.test():
        op = Ceil({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$ceil": {"$divide": ["$side_b", "$hypotenuse"]}}
