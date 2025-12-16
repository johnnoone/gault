from strata.compilers import compile_query
from strata.predicates import Type


def test_compile(context):
    predicate = Type(42)
    result = compile_query(predicate, context=context)
    assert result == {"$type": [42]}


def test_compile_unwrapped(context):
    predicate = Type([42, 12])
    result = compile_query(predicate, context=context)
    assert result == {"$type": [42, 12]}
