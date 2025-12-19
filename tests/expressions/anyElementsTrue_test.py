import pytest

from gault.expressions import AnyElementsTrue


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = AnyElementsTrue([1, 2, 3, "$a", "$b", "$c"])
        result = op.compile_expression(context=context)
        assert result == {"$anyElementsTrue": [[1, 2, 3, "$a", "$b", "$c"]]}

    with subtests.test():
        op = AnyElementsTrue("$responses")
        result = op.compile_expression(context=context)
        assert result == {"$anyElementsTrue": ["$responses"]}
