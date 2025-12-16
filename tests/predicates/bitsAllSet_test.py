from strata.compilers import compile_query
from strata.predicates import BitsAllSet


def test_compile(context):
    predicate = BitsAllSet(42)
    result = compile_query(predicate, context=context)
    assert result == {"$bitsAllSet": 42}
