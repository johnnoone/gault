import math

import pytest

from gault.expressions import Ceil


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ceil(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$ceil": math.nan}

    with subtests.test():
        op = Ceil(None)
        result = op.compile_expression(context=context)
        assert result == {"$ceil": None}

    with subtests.test():
        op = Ceil({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$ceil": {"$divide": ["$side_b", "$hypotenuse"]}}
