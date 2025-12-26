from gault import Field
from gault.window_aggregators import LinearFill


def test_expression(context):
    aggregator = LinearFill(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$linearFill": "$attr1",
    }
