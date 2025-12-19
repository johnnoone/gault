import pytest

from gault.expressions import Millisecond


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Millisecond("$date")
        result = op.compile_expression(context=context)
        assert result == {"$millisecond": {"date": "$date"}}
