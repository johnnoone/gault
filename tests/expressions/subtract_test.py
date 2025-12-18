import pytest

from strata.expressions import Subtract


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Subtract("$input1", "$input2")
        result = op.compile_expression(context=context)
        assert result == {"$subtract": ["$input1", "$input2"]}
