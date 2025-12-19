import pytest

from gault.expressions import IfNull


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = IfNull("$one", "$two", "$three")
        result = op.compile_expression(context=context)
        assert result == {"$ifNull": ["$one", "$two", "$three"]}

    with subtests.test():
        op = IfNull(["$one", "$two", "$three"])
        result = op.compile_expression(context=context)
        assert result == {"$ifNull": ["$one", "$two", "$three"]}
