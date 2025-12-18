import pytest

from strata.expressions import UnsetField


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = UnsetField("$one", "$two")
        result = op.compile_expression(context=context)
        assert result == {
            "$unsetField": {
                "input": "$one",
                "field": "$two",
            }
        }
