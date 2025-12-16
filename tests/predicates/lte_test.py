from strata.compilers import compile_query
from strata.predicates import Lte


def test_compile(context):
    predicate = Lte(42)
    result = compile_query(predicate, context=context)
    assert result == {"$lte": 42}
