import pytest

from strata.expressions import TsSecond


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = TsSecond("$one")
        result = op.compile_expression(context=context)
        assert result == {"$tsSecond": "$one"}
