import pytest

from gault.expressions import AllElementsTrue


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = AllElementsTrue([1, 2, 3, "$a", "$b", "$c"])
        result = op.compile_expression(context=context)
        assert result == {"$allElementsTrue": [[1, 2, 3, "$a", "$b", "$c"]]}

    with subtests.test():
        op = AllElementsTrue("$responses")
        result = op.compile_expression(context=context)
        assert result == {"$allElementsTrue": ["$responses"]}
