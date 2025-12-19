from gault.compilers import compile_query
from gault.predicates import JsonSchema


def test_compile(context):
    predicate = JsonSchema({"type": "object"})
    result = compile_query(predicate, context=context)
    assert result == {
        "$jsonSchema": {
            "type": "object",
        }
    }
