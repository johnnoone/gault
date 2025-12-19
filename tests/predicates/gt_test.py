from gault.compilers import compile_query
from gault.predicates import Gt


def test_compile(context):
    predicate = Gt(42)
    result = compile_query(predicate, context=context)
    assert result == {"$gt": 42}
