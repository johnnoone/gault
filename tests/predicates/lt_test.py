from gault.compilers import compile_query
from gault.predicates import Lt


def test_compile(context):
    predicate = Lt(42)
    result = compile_query(predicate, context=context)
    assert result == {"$lt": 42}
