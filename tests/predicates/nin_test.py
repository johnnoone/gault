from strata.compilers import compile_query
from strata.predicates import Nin


def test_compile(context):
    predicate = Nin(42)
    result = compile_query(predicate, context=context)
    assert result == {"$nin": [42]}


def test_compile_unwrapped(context):
    predicate = Nin([42])
    result = compile_query(predicate, context=context)
    assert result == {"$nin": [42]}
