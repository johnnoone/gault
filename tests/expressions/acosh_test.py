import math

import pytest

from gault.expressions import Acosh


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Acosh(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$acosh": math.nan}

    with subtests.test():
        op = Acosh(None)
        result = op.compile_expression(context=context)
        assert result == {"$acosh": None}

    with subtests.test():
        op = Acosh({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$acosh": {"$divide": ["$side_b", "$hypotenuse"]}}
