from gault import Field
from gault.window_aggregators import BottomN


def test_expression(context):
    aggregator = BottomN(
        sort_by=Field("attr1"),
        output=Field("attr2"),
        n=32,
    )
    assert aggregator.compile_expression(context=context) == {
        "$bottomN": {
            "n": 32,
            "output": "$attr2",
            "sortBy": {"attr1": 1},
        }
    }
