import pytest

from gault.expressions import MergeObjects


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test("__init__(single)"):
        op = MergeObjects("$input1")
        result = op.compile_expression(context=context)
        assert result == {
            "$mergeObjects": ["$input1"],
        }

    with subtests.test("__init__(one, two)"):
        op = MergeObjects("$input1", "$input2")
        result = op.compile_expression(context=context)
        assert result == {
            "$mergeObjects": [
                "$input1",
                "$input2",
            ]
        }

    with subtests.test("__init__([one])"):
        op = MergeObjects(["$input1"])
        result = op.compile_expression(context=context)
        assert result == {
            "$mergeObjects": ["$input1"],
        }

    with subtests.test("__init__([one, two])"):
        op = MergeObjects(["$input1", "$input2"])
        result = op.compile_expression(context=context)
        assert result == {
            "$mergeObjects": [
                "$input1",
                "$input2",
            ]
        }
