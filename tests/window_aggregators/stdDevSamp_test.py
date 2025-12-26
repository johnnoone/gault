from gault import Field
from gault.window_aggregators import StdDevSamp


def test_expression(context):
    aggregator = StdDevSamp(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$stdDevSamp": "$attr1",
    }
