from gault import Field
from gault.window_aggregators import ExpMovingAvg


def test_n(context):
    aggregator = ExpMovingAvg(
        input=Field("attr1"),
        n=42,
    )
    assert aggregator.compile_expression(context=context) == {
        "$expMovingAvg": {
            "input": "$attr1",
            "N": 42,
        }
    }


def test_alpha(context):
    aggregator = ExpMovingAvg(
        input=Field("attr1"),
        alpha=100,
    )
    assert aggregator.compile_expression(context=context) == {
        "$expMovingAvg": {
            "input": "$attr1",
            "alpha": 100,
        }
    }
