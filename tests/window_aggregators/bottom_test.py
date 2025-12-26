from gault import Field
from gault.window_aggregators import Bottom


def test_expression(context):
    aggregator = Bottom(
        sort_by=Field("attr1"),
        output=Field("attr2"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$bottom": {
            "output": "$attr2",
            "sortBy": {
                "attr1": 1,
            },
        }
    }
