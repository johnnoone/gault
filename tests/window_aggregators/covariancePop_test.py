from gault import Field
from gault.window_aggregators import CovariancePop


def test_expression(context):
    aggregator = CovariancePop(
        value1=Field("attr1"),
        value2=Field("attr2"),
    )
    assert aggregator.compile_expression(context=context) == {
        "$covariancePop": ["$attr1", "$attr2"],
    }
