import math

import pytest

from gault.expressions import Atanh


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Atanh(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$atanh": math.nan}

    with subtests.test():
        op = Atanh(21)
        result = op.compile_expression(context=context)
        assert result == {"$atanh": 21}

    with subtests.test():
        op = Atanh({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$atanh": {"$divide": ["$side_b", "$hypotenuse"]}}
