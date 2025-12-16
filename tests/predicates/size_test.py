from strata.compilers import compile_query
from strata.predicates import Size


def test_compile(context):
    predicate = Size(42)
    result = compile_query(predicate, context=context)
    assert result == {"$size": 42}
