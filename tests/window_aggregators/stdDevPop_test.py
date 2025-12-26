from gault import Field
from gault.window_aggregators import StdDevPop


def test_expression(context):
    aggregator = StdDevPop(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$stdDevPop": "$attr1",
    }
