from gault import Field
from gault.window_aggregators import Percentile


def test_expression(context):
    aggregator = Percentile(
        input=Field("attr1"),
        p=[1, 2, 3],
    )
    assert aggregator.compile_expression(context=context) == {
        "$percentile": {
            "input": "$attr1",
            "method": "approximate",
            "p": [1, 2, 3],
        }
    }
