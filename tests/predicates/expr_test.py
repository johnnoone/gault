from gault.compilers import compile_query
from gault.predicates import Expr


def test_compile(context):
    predicate = Expr({"$eq": ["$foo", "$bar"]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$expr": {
            "$eq": ["$foo", "$bar"],
        }
    }
