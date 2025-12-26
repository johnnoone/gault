from gault import Field
from gault.window_aggregators import Push


def test_expression(context):
    aggregator = Push(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$push": "$attr1",
    }
