from gault import Field
from gault.window_aggregators import Sum


def test_expression(context):
    aggregator = Sum(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$sum": "$attr1",
    }
