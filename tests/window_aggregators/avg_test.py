from gault import Field
from gault.window_aggregators import Avg


def test_expression(context):
    aggregator = Avg(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$avg": "$attr1",
    }
