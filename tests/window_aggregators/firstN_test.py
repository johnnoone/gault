from gault import Field
from gault.window_aggregators import FirstN


def test_expression(context):
    aggregator = FirstN(
        input=Field("attr1"),
        n=Field("attr2"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$firstN": {
            "input": "$attr1",
            "n": "$attr2",
        }
    }
