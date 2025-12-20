import pytest

from gault.expressions import Max


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test("__init__(single)"):
        op = Max("$input1")
        result = op.compile_expression(context=context)
        assert result == {
            "$max": "$input1",
        }

    with subtests.test("__init__(one, two)"):
        op = Max("$input1", "$input2")
        result = op.compile_expression(context=context)
        assert result == {
            "$max": [
                "$input1",
                "$input2",
            ]
        }

    with subtests.test("__init__([one])"):
        op = Max(["$input1"])
        result = op.compile_expression(context=context)
        assert result == {
            "$max": ["$input1"],
        }

    with subtests.test("__init__([one, two])"):
        op = Max(["$input1", "$input2"])
        result = op.compile_expression(context=context)
        assert result == {
            "$max": [
                "$input1",
                "$input2",
            ]
        }
