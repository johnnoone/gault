from gault import Field
from gault.window_aggregators import Integral


def test_number_expression(context):
    aggregator = Integral(
        input=Field("attr1"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$integral": {
            "input": "$attr1",
        }
    }


def test_date_expression(context):
    aggregator = Integral(
        input=Field("attr1"),
        unit="hour",
    )
    assert aggregator.compile_expression(context=context) == {
        "$integral": {
            "input": "$attr1",
            "unit": "hour",
        }
    }
