from gault import Field
from gault.window_aggregators import Derivative


def test_expression(context):
    aggregator = Derivative(
        input=Field("attr1"),
        unit="millisecond",
    )
    assert aggregator.compile_expression(context=context) == {
        "$derivative": {
            "input": "$attr1",
            "unit": "millisecond",
        }
    }
