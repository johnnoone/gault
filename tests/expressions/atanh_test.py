import math

import pytest

from strata.expressions import Atanh


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Atanh(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$atanh": math.nan}

    with subtests.test():
        op = Atanh(None)
        result = op.compile_expression(context=context)
        assert result == {"$atanh": None}

    with subtests.test():
        op = Atanh({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$atanh": {"$divide": ["$side_b", "$hypotenuse"]}}
