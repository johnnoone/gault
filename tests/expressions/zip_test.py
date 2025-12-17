import pytest

from strata.compilers import CompilationError
from strata.expressions import Zip, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Zip(
            inputs=["$one", "$two"],
            use_longest_length=True,
            defaults="$three",
        )
        result = compile_expression(op, context=context)
        assert result == {
            "$zip": {
                "defaults": "$three",
                "inputs": ["$one", "$two"],
                "useLongestLength": True,
            }
        }


def test_query(context, subtests: pytest.Subtests):
    op = Zip(
        inputs=["$one", "$two"],
        use_longest_length=True,
        defaults="$three",
    )
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
