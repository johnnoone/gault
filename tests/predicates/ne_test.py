from gault.compilers import compile_query
from gault.predicates import Ne


def test_compile(context):
    predicate = Ne(42)
    result = compile_query(predicate, context=context)
    assert result == {"$ne": 42}
