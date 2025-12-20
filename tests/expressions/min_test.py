import pytest

from gault.expressions import Min


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test("__init__(single)"):
        op = Min("$input1")
        result = op.compile_expression(context=context)
        assert result == {
            "$min": "$input1",
        }

    with subtests.test("__init__(one, two)"):
        op = Min("$input1", "$input2")
        result = op.compile_expression(context=context)
        assert result == {
            "$min": [
                "$input1",
                "$input2",
            ]
        }

    with subtests.test("__init__([one])"):
        op = Min(["$input1"])
        result = op.compile_expression(context=context)
        assert result == {
            "$min": ["$input1"],
        }

    with subtests.test("__init__([one, two])"):
        op = Min(["$input1", "$input2"])
        result = op.compile_expression(context=context)
        assert result == {
            "$min": [
                "$input1",
                "$input2",
            ]
        }
