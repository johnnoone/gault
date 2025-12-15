import pytest
from strata.expressions import (
    ArrayToObject,
    CompilationError,
    Literal,
    compile_expression,
    compile_query,
)


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ArrayToObject("$responses")
        result = compile_expression(op, context=context)
        assert result == {"$arrayToObject": "$responses"}

    with subtests.test():
        op = ArrayToObject([["item", "abc123"], ["qty", 25]])
        result = compile_expression(op, context=context)
        assert result == {"$arrayToObject": [["item", "abc123"], ["qty", 25]]}

    with subtests.test():
        op = ArrayToObject([{"k": "item", "v": "abc123"}, {"k": "qty", "v": 25}])
        result = compile_expression(op, context=context)
        assert result == {
            "$arrayToObject": [{"k": "item", "v": "abc123"}, {"k": "qty", "v": 25}]
        }

    with subtests.test():
        op = ArrayToObject(Literal([["item", "abc123"], ["qty", 25]]))
        result = compile_expression(op, context=context)
        assert result == {
            "$arrayToObject": {"$literal": [["item", "abc123"], ["qty", 25]]}
        }

    with subtests.test():
        op = ArrayToObject({"$literal": [["item", "abc123"], ["qty", 25]]})
        result = compile_expression(op, context=context)
        assert result == {
            "$arrayToObject": {"$literal": [["item", "abc123"], ["qty", 25]]}
        }


def test_query(context, subtests: pytest.Subtests):
    op = ArrayToObject([1, 2, 3, "$a", "$b", "$c"])
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
