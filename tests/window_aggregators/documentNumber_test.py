from gault.window_aggregators import DocumentNumber


def test_expression(context):
    aggregator = DocumentNumber()
    assert aggregator.compile_expression(context=context) == {
        "$documentNumber": {},
    }
