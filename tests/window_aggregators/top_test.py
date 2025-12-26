from gault import Field
from gault.window_aggregators import Top


def test_expression(context):
    aggregator = Top(
        sort_by=Field("attr1"),
        output=Field("attr2"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$top": {
            "output": "$attr2",
            "sortBy": {
                "attr1": 1,
            },
        }
    }
