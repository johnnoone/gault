import pytest
from strata.expressions import In, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = In("$one", "$two")
        result = compile_expression(op, context=context)
        assert result == {"$in": ["$one", "$two"]}


def test_query(context, subtests: pytest.Subtests):
    op = In("one", "$two")
    result = compile_query(op, context=context)
    assert result == {"one": {"$in": "$two"}}
