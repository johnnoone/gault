from gault.compilers import compile_query
from gault.predicates import BitsAllClear


def test_compile(context):
    predicate = BitsAllClear(42)
    result = compile_query(predicate, context=context)
    assert result == {"$bitsAllClear": 42}
