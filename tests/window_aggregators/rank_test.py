from gault.window_aggregators import Rank


def test_expression(context):
    aggregator = Rank()
    assert aggregator.compile_expression(context=context) == {
        "$rank": {},
    }
