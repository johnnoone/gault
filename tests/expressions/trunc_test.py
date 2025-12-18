import pytest

from strata.expressions import Trunc


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Trunc("$one", "$place")
        result = op.compile_expression(context=context)
        assert result == {"$trunc": ["$one", "$place"]}
