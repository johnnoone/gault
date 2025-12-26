from gault import Field
from gault.window_aggregators import SetUnion


def test_expression(context):
    aggregator = SetUnion(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$setUnion": "$attr1",
    }
