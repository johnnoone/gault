from gault import Field
from gault.window_aggregators import Shift


def test_expression(context):
    aggregator = Shift(
        by=Field("attr1"),
        output=Field("attr2"),
        default=42,
    )
    assert aggregator.compile_expression(context=context) == {
        "$shift": {
            "output": "$attr2",
            "by": "$attr1",
            "default": 42,
        }
    }
