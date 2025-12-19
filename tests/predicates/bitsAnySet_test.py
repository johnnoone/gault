from gault.compilers import compile_query
from gault.predicates import BitsAnySet


def test_compile(context):
    predicate = BitsAnySet(42)
    result = compile_query(predicate, context=context)
    assert result == {"$bitsAnySet": 42}
