from gault import Field
from gault.window_aggregators import Min


def test_expression(context):
    aggregator = Min(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$min": "$attr1",
    }
