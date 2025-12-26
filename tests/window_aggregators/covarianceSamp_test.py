from gault import Field
from gault.window_aggregators import CovarianceSamp


def test_expression(context):
    aggregator = CovarianceSamp(
        value1=Field("attr1"),
        value2=Field("attr2"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$covarianceSamp": ["$attr1", "$attr2"],
    }
