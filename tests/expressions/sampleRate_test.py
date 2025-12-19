import pytest

from gault.expressions import SampleRate


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SampleRate("$var")
        result = op.compile_expression(context=context)
        assert result == {
            "$sampleRate": "$var",
        }
