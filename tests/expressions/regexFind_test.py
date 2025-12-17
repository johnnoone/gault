import pytest

from strata.compilers import CompilationError
from strata.expressions import RegexFind, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = RegexFind(
            input="$category",
            regex="cafe",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$regexFind": {
                "input": "$category",
                "regex": "cafe",
            },
        }


def test_query(context, subtests: pytest.Subtests):
    op = RegexFind(
        input="$category",
        regex="cafe",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
