import pytest

from gault.expressions import Abs


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Abs("$field")
        result = op.compile_expression(context=context)
        assert result == {"$abs": "$field"}

    with subtests.test():
        op = Abs(-1)
        result = op.compile_expression(context=context)
        assert result == {"$abs": -1}

    with subtests.test():
        op = Abs("$other")
        result = op.compile_expression(context=context)
        assert result == {"$abs": "$other"}

    with subtests.test():
        op = Abs(12)
        result = op.compile_expression(context=context)
        assert result == {"$abs": 12}

    with subtests.test():
        op = Abs({"$subtract": ["$startTemp", "$endTemp"]})
        result = op.compile_expression(context=context)
        assert result == {"$abs": {"$subtract": ["$startTemp", "$endTemp"]}}
