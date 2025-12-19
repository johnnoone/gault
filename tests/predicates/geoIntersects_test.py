from gault.compilers import compile_query
from gault.predicates import GeoIntersects


def test_compile(context):
    predicate = GeoIntersects({"$box": [[0, 0], [1, 1]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoIntersects": {
            "$box": [
                [0, 0],
                [1, 1],
            ],
        }
    }
