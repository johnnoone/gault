import pytest

from strata.expressions import Slice


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Slice("$input", n="$n", position="$pos")
        result = op.compile_expression(context=context)
        assert result == {"$slice": ["$input", "$pos", "$n"]}

    with subtests.test():
        op = Slice("$input", n="$n")
        result = op.compile_expression(context=context)
        assert result == {"$slice": ["$input", "$n"]}
