import pytest

from strata.expressions import SampleRate, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = SampleRate("$var")
        result = compile_expression(op, context=context)
        assert result == {
            "$sampleRate": "$var",
        }


def test_query(context, subtests: pytest.Subtests):
    op = SampleRate("$var")
    result = compile_query(op, context=context)
    assert result == {
        "$sampleRate": "$var",
    }
