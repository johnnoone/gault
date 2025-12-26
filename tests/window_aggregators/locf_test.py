from gault import Field
from gault.window_aggregators import Locf


def test_expression(context):
    aggregator = Locf(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$locf": "$attr1",
    }
