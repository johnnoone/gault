from gault import Field
from gault.window_aggregators import Last


def test_expression(context):
    aggregator = Last(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$last": "$attr1",
    }
