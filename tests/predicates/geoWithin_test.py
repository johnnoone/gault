from gault.compilers import compile_query
from gault.predicates import GeoWithin


def test_box(context):
    predicate = GeoWithin({"$box": [[0, 0], [1, 1]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoWithin": {
            "$box": [
                [0, 0],
                [1, 1],
            ]
        }
    }


def test_polygon(context):
    predicate = GeoWithin({"$polygon": [[0, 0], [1, 1]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoWithin": {
            "$polygon": [
                [0, 0],
                [1, 1],
            ]
        }
    }


def test_center(context):
    predicate = GeoWithin({"$center": [[0, 0], [1, 1]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoWithin": {
            "$center": [
                [0, 0],
                [1, 1],
            ]
        }
    }


def test_centerSphere(context):
    predicate = GeoWithin({"$centerSphere": [[0, 0], [1, 1]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoWithin": {
            "$centerSphere": [
                [0, 0],
                [1, 1],
            ]
        }
    }


def test_geojson_polygon(context):
    predicate = GeoWithin({"type": "Polygon", "coordinates": [[0, 0], [1, 1]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoWithin": {
            "$geometry": {
                "type": "Polygon",
                "coordinates": [
                    [0, 0],
                    [1, 1],
                ],
            }
        }
    }


def test_geojson_multipolygon(context):
    predicate = GeoWithin(
        {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [0, 0],
                    [1, 1],
                ],
            ],
        }
    )
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoWithin": {
            "$geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [0, 0],
                        [1, 1],
                    ]
                ],
            }
        }
    }
