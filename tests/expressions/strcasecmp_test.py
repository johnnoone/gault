import pytest

from strata.expressions import StrCaseCmp


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = StrCaseCmp("$input1", "$input2")
        result = op.compile_expression(context=context)
        assert result == {"$strcasecmp": ["$input1", "$input2"]}
