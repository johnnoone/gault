import math

import pytest

from strata.expressions import Exp


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Exp(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$exp": math.nan}

    with subtests.test():
        op = Exp(None)
        result = op.compile_expression(context=context)
        assert result == {"$exp": None}

    with subtests.test():
        op = Exp({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$exp": {"$divide": ["$side_b", "$hypotenuse"]}}
