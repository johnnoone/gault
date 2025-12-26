from gault import Field
from gault.window_aggregators import MinN


def test_expression(context):
    aggregator = MinN(
        input=Field("attr1"),
        n=42,
    )
    assert aggregator.compile_expression(context=context) == {
        "$minN": {
            "input": "$attr1",
            "n": 42,
        }
    }
