import pytest

from strata.expressions import RegexFind


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = RegexFind(
            input="$category",
            regex="cafe",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$regexFind": {
                "input": "$category",
                "regex": "cafe",
            },
        }
