from gault import Field
from gault.window_aggregators import MaxN


def test_expression(context):
    aggregator = MaxN(
        input=Field("attr1"),
        n=42,
    )
    assert aggregator.compile_expression(context=context) == {
        "$maxN": {
            "input": "$attr1",
            "n": 42,
        }
    }
