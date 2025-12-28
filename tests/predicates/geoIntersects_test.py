from gault.compilers import compile_query
from gault.predicates import GeoIntersects


def test_compile(context):
    predicate = GeoIntersects(
        {
            "type": "Polygon",
            "coordinates": [
                [0, 0],
                [1, 1],
            ],
        }  # ty:ignore[invalid-argument-type]
    )
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoIntersects": {
            "$geometry": {
                "type": "Polygon",
                "coordinates": [
                    [0, 0],
                    [1, 1],
                ],
            }
        }
    }
