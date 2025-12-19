from gault.compilers import compile_query
from gault.predicates import Eq


def test_compile(context):
    predicate = Eq(42)
    result = compile_query(predicate, context=context)
    assert result == {"$eq": 42}
