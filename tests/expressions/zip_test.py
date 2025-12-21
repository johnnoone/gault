import pytest

from gault.expressions import Zip


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Zip(
            inputs=["$one", "$two"],
            use_longest_length=True,
            defaults=["$three"],
        )
        result = op.compile_expression(context=context)
        assert result == {
            "$zip": {
                "defaults": ["$three"],
                "inputs": ["$one", "$two"],
                "useLongestLength": True,
            }
        }
