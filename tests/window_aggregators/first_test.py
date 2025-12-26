from gault import Field
from gault.window_aggregators import First


def test_expression(context):
    aggregator = First(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$first": "$attr1",
    }
