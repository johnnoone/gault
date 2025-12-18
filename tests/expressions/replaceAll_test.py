import pytest

from strata.expressions import ReplaceAll


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ReplaceAll(
            input="$category",
            find="cafe",
            replacement="croissant",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$replaceAll": {
                "input": "$category",
                "find": "cafe",
                "replacement": "croissant",
            },
        }
