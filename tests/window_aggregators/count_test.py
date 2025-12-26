from gault import Field
from gault.window_aggregators import Count


def test_expression(context):
    aggregator = Count()
    assert aggregator.compile_expression(context=context) == {
        "$count": {},
    }
