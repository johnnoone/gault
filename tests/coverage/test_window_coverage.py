from __future__ import annotations

import pytest

from gault import Field
from gault.window_aggregators import Avg, ExpMovingAvg


def test_window_operator_with_documents(context):
    """Line 51: WindowOperator with window_documents."""
    aggregator = Avg(
        input=Field("attr1"),
        window_documents=("unbounded", "current"),
    )
    result = aggregator.compile_expression(context=context)
    assert result == {
        "$avg": "$attr1",
        "documents": ["unbounded", "current"],
    }


def test_window_operator_with_range(context):
    """Line 53: WindowOperator with window_range."""
    aggregator = Avg(
        input=Field("attr1"),
        window_range=(-10, 0),
    )
    result = aggregator.compile_expression(context=context)
    assert result == {
        "$avg": "$attr1",
        "range": [-10, 0],
    }


def test_window_operator_with_unit(context):
    """Line 55: WindowOperator with window_unit."""
    aggregator = Avg(
        input=Field("attr1"),
        window_range=("unbounded", "current"),
        window_unit="day",
    )
    result = aggregator.compile_expression(context=context)
    assert result == {
        "$avg": "$attr1",
        "range": ["unbounded", "current"],
        "unit": "day",
    }


def test_exp_moving_avg_with_both_n_and_alpha():
    """Lines 424-425: ExpMovingAvg with both n and alpha raises TypeError."""
    with pytest.raises(TypeError, match="n or alpha, not both"):
        ExpMovingAvg(input=Field("attr1"), n=10, alpha=0.5)


def test_exp_moving_avg_with_neither_n_nor_alpha():
    """Lines 428-429: ExpMovingAvg with neither n nor alpha raises TypeError."""
    with pytest.raises(TypeError, match="n or alpha required"):
        ExpMovingAvg(input=Field("attr1"))
