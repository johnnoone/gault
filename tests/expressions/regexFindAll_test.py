import pytest

from strata.expressions import RegexFindAll


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = RegexFindAll(
            input="$category",
            regex="cafe",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$regexFindAll": {
                "input": "$category",
                "regex": "cafe",
            },
        }
