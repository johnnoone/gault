import pytest

from strata.expressions import ArrayToObject, Literal


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = ArrayToObject("$responses")
        result = op.compile_expression(context=context)
        assert result == {"$arrayToObject": "$responses"}

    with subtests.test():
        op = ArrayToObject([["item", "abc123"], ["qty", 25]])
        result = op.compile_expression(context=context)
        assert result == {"$arrayToObject": [["item", "abc123"], ["qty", 25]]}

    with subtests.test():
        op = ArrayToObject([{"k": "item", "v": "abc123"}, {"k": "qty", "v": 25}])
        result = op.compile_expression(context=context)
        assert result == {
            "$arrayToObject": [{"k": "item", "v": "abc123"}, {"k": "qty", "v": 25}]
        }

    with subtests.test():
        op = ArrayToObject(Literal([["item", "abc123"], ["qty", 25]]))
        result = op.compile_expression(context=context)
        assert result == {
            "$arrayToObject": {"$literal": [["item", "abc123"], ["qty", 25]]}
        }

    with subtests.test():
        op = ArrayToObject({"$literal": [["item", "abc123"], ["qty", 25]]})
        result = op.compile_expression(context=context)
        assert result == {
            "$arrayToObject": {"$literal": [["item", "abc123"], ["qty", 25]]}
        }
