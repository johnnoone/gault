from gault import Field
from gault.window_aggregators import ConcatArrays


def test_expression(context):
    aggregator = ConcatArrays(
        field=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$concatArrays": "$attr1",
    }
