from gault import Field
from gault.window_aggregators import AddToSet


def test_expression(context):
    aggregator = AddToSet(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$addToSet": "$attr1",
    }
