import pytest

from strata.expressions import Minute


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Minute("$date")
        result = op.compile_expression(context=context)
        assert result == {"$minute": {"date": "$date"}}
