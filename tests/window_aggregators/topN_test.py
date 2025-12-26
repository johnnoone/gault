from gault import Field
from gault.window_aggregators import TopN


def test_expression(context):
    aggregator = TopN(
        sort_by=Field("attr1"),
        output=Field("attr2"),
        n=42,
    )
    assert aggregator.compile_expression(context=context) == {
        "$topN": {
            "n": 42,
            "output": "$attr2",
            "sortBy": {
                "attr1": 1,
            },
        }
    }
