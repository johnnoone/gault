from gault.geo import compile_geo
from gault.shapes import Box, Center, CenterSphere, Coordinates, Polygon


def test_box(context):
    geo = Box(Coordinates(1, 2), Coordinates(3, 4))
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$box": [
            [1, 2],
            [3, 4],
        ]
    }


def test_center(context):
    geo = Center(1, 2, radius=42)
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$center": [
            [1, 2],
            42,
        ]
    }


def test_center_sphere(context):
    geo = CenterSphere(1, 2, radius=42)
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$centerSphere": [
            [1, 2],
            42,
        ]
    }


def test_polygon(context):
    geo = Polygon(
        points=[
            Coordinates(1, 2),
            Coordinates(3, 4),
            Coordinates(5, 6),
            Coordinates(1, 2),
        ]
    )
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$polygon": [
            [1, 2],
            [3, 4],
            [5, 6],
            [1, 2],
        ],
    }
