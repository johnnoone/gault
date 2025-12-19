from gault.compilers import compile_query
from gault.predicates import Mod


def test_compile(context):
    predicate = Mod(12, 42)
    result = compile_query(predicate, context=context)
    assert result == {
        "$mod": [12, 42],
    }
