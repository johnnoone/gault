from gault.compilers import compile_query
from gault.predicates import Eq, Not


def test_compile(context):
    predicate = Not(
        Eq("value"),
    )
    result = compile_query(predicate, context=context)
    assert result == {"$not": {"$eq": "value"}}


def test_compile_inverse(context):
    predicate = ~Not(
        Eq("value"),
    )

    result = compile_query(predicate, context=context)
    assert result == {"$eq": "value"}
