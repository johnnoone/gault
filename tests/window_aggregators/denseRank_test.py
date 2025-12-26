from gault import Field
from gault.window_aggregators import DenseRank


def test_expression(context):
    aggregator = DenseRank()
    assert aggregator.compile_expression(context=context) == {
        "$denseRank": {},
    }
