from strata.compilers import compile_query
from strata.predicates import BitsAllClear


def test_compile(context):
    predicate = BitsAllClear(42)
    result = compile_query(predicate, context=context)
    assert result == {"$bitsAllClear": 42}
