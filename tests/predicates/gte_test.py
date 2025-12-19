from gault.compilers import compile_query
from gault.predicates import Gte


def test_compile(context):
    predicate = Gte(42)
    result = compile_query(predicate, context=context)
    assert result == {"$gte": 42}
