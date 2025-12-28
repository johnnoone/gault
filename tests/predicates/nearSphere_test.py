from gault.compilers import compile_query
from gault.predicates import NearSphere
from gault.geo import Point
from gault.shapes import Coordinates


def test_point_dict(context):
    predicate = NearSphere(
        {
            "type": "Point",
            "coordinates": [0, 1],
        },
        min_distance=12,
        max_distance=42,
    )
    result = compile_query(predicate, context=context)
    assert result == {
        "$nearSphere": {
            "$geometry": {
                "type": "Point",
                "coordinates": [0, 1],
            },
            "$maxDistance": 42,
            "$minDistance": 12,
        },
    }


def test_point(context):
    predicate = NearSphere(
        Point(0, 1),
        min_distance=12,
        max_distance=42,
    )
    result = compile_query(predicate, context=context)
    assert result == {
        "$nearSphere": {
            "$geometry": {
                "type": "Point",
                "coordinates": [0, 1],
            },
            "$maxDistance": 42,
            "$minDistance": 12,
        },
    }


def test_coordinates(context):
    predicate = NearSphere(
        Coordinates(0, 1),
        min_distance=12,
        max_distance=42,
    )
    result = compile_query(predicate, context=context)
    assert result == {
        "$nearSphere": {
            "$geometry": {
                "type": "Point",
                "coordinates": [0, 1],
            },
            "$maxDistance": 42,
            "$minDistance": 12,
        },
    }
