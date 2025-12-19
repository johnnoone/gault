from strata.compilers import compile_query
from strata.predicates import Exists


def test_compile(context):
    predicate = Exists(True)
    result = compile_query(predicate, context=context)
    assert result == {"$exists": True}
