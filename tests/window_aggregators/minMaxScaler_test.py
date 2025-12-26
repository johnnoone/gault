from gault import Field
from gault.window_aggregators import MinMaxScaler


def test_expression(context):
    aggregator = MinMaxScaler(
        input=Field("attr1"),
        min=0,
        max=42,
    )
    assert aggregator.compile_expression(context=context) == {
        "$minMaxScaler": {
            "input": "$attr1",
            "max": 42,
            "min": 0,
        }
    }
