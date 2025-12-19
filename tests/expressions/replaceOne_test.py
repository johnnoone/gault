import pytest

from gault.expressions import ReplaceOne


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ReplaceOne(
            input="$category",
            find="cafe",
            replacement="croissant",
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$replaceOne": {
                "input": "$category",
                "find": "cafe",
                "replacement": "croissant",
            },
        }
