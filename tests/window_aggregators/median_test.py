from gault import Field
from gault.window_aggregators import Median


def test_expression(context):
    aggregator = Median(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$median": {
            "input": "$attr1",
            "method": "approximate",
        }
    }
