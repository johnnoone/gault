import math

import pytest

from gault.expressions import Ln


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Ln(math.nan)
        result = op.compile_expression(context=context)
        assert result == {"$ln": math.nan}

    with subtests.test():
        op = Ln(None)
        result = op.compile_expression(context=context)
        assert result == {"$ln": None}

    with subtests.test():
        op = Ln({"$divide": ["$side_b", "$hypotenuse"]})
        result = op.compile_expression(context=context)
        assert result == {"$ln": {"$divide": ["$side_b", "$hypotenuse"]}}
