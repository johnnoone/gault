from gault.compilers import compile_query
from gault.predicates import In


def test_compile(context):
    predicate = In(42)
    result = compile_query(predicate, context=context)
    assert result == {"$in": [42]}


def test_compile_unwrapped(context):
    predicate = In([42])
    result = compile_query(predicate, context=context)
    assert result == {"$in": [42]}
