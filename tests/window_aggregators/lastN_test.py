from gault import Field
from gault.window_aggregators import LastN


def test_expression(context):
    aggregator = LastN(
        input=Field("attr1"),
        n=Field("attr2"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$lastN": {
            "input": "$attr1",
            "n": "$attr2",
        }
    }
