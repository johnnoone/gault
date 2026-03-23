from __future__ import annotations

import pytest

from gault.geo import (
    GeometryCollection,
    LineString,
    MultiPolygon,
    Point,
    Polygon,
    compile_geo,
)


def test_compile_geo_with_geojson_dict(context):
    """Line 87: compile_geo with GeoJSON dict passthrough via $geometry key."""
    geo = {"$geometry": {"type": "Point", "coordinates": [40, 5]}}
    result = compile_geo(geo, context=context)
    assert result == {"$geometry": {"type": "Point", "coordinates": [40, 5]}}


def test_compile_geo_with_invalid_type(context):
    """Lines 110-111: compile_geo with invalid type raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        compile_geo(42, context=context)


def test_polygon_with_crs(context):
    """Line 162: Polygon with crs compiles custom dict."""
    geo = Polygon(
        [LineString([Point(0, 0), Point(3, 6), Point(6, 1), Point(0, 0)])],
        crs="urn:x-mongodb:crs:strictwinding:EPSG:4326",
    )
    result = compile_geo(geo, context=context)
    assert result == {
        "$geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [3, 6], [6, 1], [0, 0]]],
            "crs": {
                "type": "name",
                "properties": {"name": "urn:x-mongodb:crs:strictwinding:EPSG:4326"},
            },
        },
    }


def test_multi_polygon_with_crs(context):
    """Line 221: MultiPolygon with crs compiles custom dict."""
    geo = MultiPolygon(
        [
            Polygon(
                [LineString([Point(0, 0), Point(3, 6), Point(6, 1), Point(0, 0)])]
            ),
        ],
        crs="urn:x-mongodb:crs:strictwinding:EPSG:4326",
    )
    result = compile_geo(geo, context=context)
    assert result == {
        "$geometry": {
            "type": "MultiPolygon",
            "coordinates": [[[[0, 0], [3, 6], [6, 1], [0, 0]]]],
            "crs": {
                "type": "name",
                "properties": {"name": "urn:x-mongodb:crs:strictwinding:EPSG:4326"},
            },
        },
    }


def test_geometry_collection_get_coordinates():
    """Line 257: GeometryCollection.get_coordinates."""
    geo = GeometryCollection(
        [
            Point(1, 2),
            Point(3, 4),
        ]
    )
    assert geo.get_coordinates() == [[1, 2], [3, 4]]
