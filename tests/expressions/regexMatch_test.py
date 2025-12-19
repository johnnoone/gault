import pytest

from gault.expressions import RegexMatch


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = RegexMatch(
            input="$category",
            regex="cafe",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$regexMatch": {
                "input": "$category",
                "regex": "cafe",
            },
        }
