from gault.compilers import compile_query
from gault.predicates import Near


def test_compile(context):
    predicate = Near({"$box": [[0, 0], [1, 1]]}, min_distance=12, max_distance=42)
    result = compile_query(predicate, context=context)
    assert result == {
        "$near": {
            "$box": [
                [0, 0],
                [1, 1],
            ],
        },
        "$maxDistance": 42,
        "$minDistance": 12,
    }
