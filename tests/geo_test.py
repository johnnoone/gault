from gault.geo import compile_geo
from gault.geo import (
    Point,
    LineString,
    Polygon,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    GeometryCollection,
)


def test_compile_point(context):
    geo = Point(40, 5)
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "Point",
            "coordinates": [40, 5],
        }
    }


def test_compile_line_string(context):
    geo = LineString([Point(40, 5), Point(41, 6)])
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "LineString",
            "coordinates": [[40, 5], [41, 6]],
        }
    }


def test_compile_polygon_single_ring(context):
    geo = Polygon([LineString([Point(0, 0), Point(3, 6), Point(6, 1), Point(0, 0)])])
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [3, 6], [6, 1], [0, 0]]],
        }
    }


def test_compile_polygon_multi_rings(context):
    geo = Polygon(
        [
            LineString([Point(0, 0), Point(3, 6), Point(6, 1), Point(0, 0)]),
            LineString([Point(2, 2), Point(3, 3), Point(4, 2), Point(2, 2)]),
        ],
    )
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "Polygon",
            "coordinates": [
                [[0, 0], [3, 6], [6, 1], [0, 0]],
                [[2, 2], [3, 3], [4, 2], [2, 2]],
            ],
        }
    }


def test_compile_multi_point(context):
    geo = MultiPoint(
        [
            Point(-73.9580, 40.8003),
            Point(-73.9498, 40.7968),
            Point(-73.9737, 40.7648),
            Point(-73.9814, 40.7681),
        ],
    )
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "MultiPoint",
            "coordinates": [
                [-73.9580, 40.8003],
                [-73.9498, 40.7968],
                [-73.9737, 40.7648],
                [-73.9814, 40.7681],
            ],
        }
    }


def test_compile_multi_line_string(context):
    geo = MultiLineString(
        [
            LineString([Point(-73.96943, 40.78519), Point(-73.96082, 40.78095)]),
            LineString([Point(-73.96415, 40.79229), Point(-73.95544, 40.78854)]),
            LineString([Point(-73.97162, 40.78205), Point(-73.96374, 40.77715)]),
            LineString([Point(-73.97880, 40.77247), Point(-73.97036, 40.76811)]),
        ],
    )
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "MultiLineString",
            "coordinates": [
                [[-73.96943, 40.78519], [-73.96082, 40.78095]],
                [[-73.96415, 40.79229], [-73.95544, 40.78854]],
                [[-73.97162, 40.78205], [-73.96374, 40.77715]],
                [[-73.97880, 40.77247], [-73.97036, 40.76811]],
            ],
        }
    }


def test_compile_multi_polygon(context):
    geo = MultiPolygon(
        [
            Polygon(
                [
                    LineString(
                        [
                            Point(-73.958, 40.8003),
                            Point(-73.9498, 40.7968),
                            Point(-73.9737, 40.7648),
                            Point(-73.9814, 40.7681),
                            Point(-73.958, 40.8003),
                        ]
                    ),
                ]
            ),
            Polygon(
                [
                    LineString(
                        [
                            Point(-73.958, 40.8003),
                            Point(-73.9498, 40.7968),
                            Point(-73.9737, 40.7648),
                            Point(-73.958, 40.8003),
                        ]
                    )
                ]
            ),
        ]
    )
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [-73.958, 40.8003],
                        [-73.9498, 40.7968],
                        [-73.9737, 40.7648],
                        [-73.9814, 40.7681],
                        [-73.958, 40.8003],
                    ]
                ],
                [
                    [
                        [-73.958, 40.8003],
                        [-73.9498, 40.7968],
                        [-73.9737, 40.7648],
                        [-73.958, 40.8003],
                    ]
                ],
            ],
        }
    }


def test_compile_geometry_collection(context):
    geo = GeometryCollection(
        [
            MultiPoint(
                [
                    Point(-73.9580, 40.8003),
                    Point(-73.9498, 40.7968),
                    Point(-73.9737, 40.7648),
                    Point(-73.9814, 40.7681),
                ],
            ),
            MultiLineString(
                [
                    LineString(
                        [
                            Point(-73.96943, 40.78519),
                            Point(-73.96082, 40.78095),
                        ]
                    ),
                    LineString(
                        [
                            Point(-73.96415, 40.79229),
                            Point(-73.95544, 40.78854),
                        ]
                    ),
                    LineString(
                        [
                            Point(-73.97162, 40.78205),
                            Point(-73.96374, 40.77715),
                        ]
                    ),
                    LineString(
                        [
                            Point(-73.97880, 40.77247),
                            Point(-73.97036, 40.76811),
                        ]
                    ),
                ],
            ),
        ]
    )
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "MultiPoint",
                    "coordinates": [
                        [-73.9580, 40.8003],
                        [-73.9498, 40.7968],
                        [-73.9737, 40.7648],
                        [-73.9814, 40.7681],
                    ],
                },
                {
                    "type": "MultiLineString",
                    "coordinates": [
                        [[-73.96943, 40.78519], [-73.96082, 40.78095]],
                        [[-73.96415, 40.79229], [-73.95544, 40.78854]],
                        [[-73.97162, 40.78205], [-73.96374, 40.77715]],
                        [[-73.97880, 40.77247], [-73.97036, 40.76811]],
                    ],
                },
            ],
        }
    }


####


def test_compile_geojson_point(context):
    geo = {"type": "Point", "coordinates": [40, 5]}
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "Point",
            "coordinates": [40, 5],
        }
    }


def test_compile_geojson_line_string(context):
    geo = {"type": "LineString", "coordinates": [[40, 5], [41, 6]]}
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "LineString",
            "coordinates": [[40, 5], [41, 6]],
        }
    }


def test_compile_geojson_polygon_single_ring(context):
    geo = {"type": "Polygon", "coordinates": [[[0, 0], [3, 6], [6, 1], [0, 0]]]}
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [3, 6], [6, 1], [0, 0]]],
        }
    }


def test_compile_geojson_polygon_multi_rings(context):
    geo = {
        "type": "Polygon",
        "coordinates": [
            [[0, 0], [3, 6], [6, 1], [0, 0]],
            [[2, 2], [3, 3], [4, 2], [2, 2]],
        ],
    }
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "Polygon",
            "coordinates": [
                [[0, 0], [3, 6], [6, 1], [0, 0]],
                [[2, 2], [3, 3], [4, 2], [2, 2]],
            ],
        }
    }


def test_compile_geojson_multi_point(context):
    geo = {
        "type": "MultiPoint",
        "coordinates": [
            [-73.9580, 40.8003],
            [-73.9498, 40.7968],
            [-73.9737, 40.7648],
            [-73.9814, 40.7681],
        ],
    }
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "MultiPoint",
            "coordinates": [
                [-73.9580, 40.8003],
                [-73.9498, 40.7968],
                [-73.9737, 40.7648],
                [-73.9814, 40.7681],
            ],
        }
    }


def test_compile_geojson_multi_line_string(context):
    geo = {
        "type": "MultiLineString",
        "coordinates": [
            [[-73.96943, 40.78519], [-73.96082, 40.78095]],
            [[-73.96415, 40.79229], [-73.95544, 40.78854]],
            [[-73.97162, 40.78205], [-73.96374, 40.77715]],
            [[-73.97880, 40.77247], [-73.97036, 40.76811]],
        ],
    }
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "MultiLineString",
            "coordinates": [
                [[-73.96943, 40.78519], [-73.96082, 40.78095]],
                [[-73.96415, 40.79229], [-73.95544, 40.78854]],
                [[-73.97162, 40.78205], [-73.96374, 40.77715]],
                [[-73.97880, 40.77247], [-73.97036, 40.76811]],
            ],
        }
    }


def test_compile_geojson_multi_polygon(context):
    geo = {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [-73.958, 40.8003],
                    [-73.9498, 40.7968],
                    [-73.9737, 40.7648],
                    [-73.9814, 40.7681],
                    [-73.958, 40.8003],
                ]
            ],
            [
                [
                    [-73.958, 40.8003],
                    [-73.9498, 40.7968],
                    [-73.9737, 40.7648],
                    [-73.958, 40.8003],
                ]
            ],
        ],
    }
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [-73.958, 40.8003],
                        [-73.9498, 40.7968],
                        [-73.9737, 40.7648],
                        [-73.9814, 40.7681],
                        [-73.958, 40.8003],
                    ]
                ],
                [
                    [
                        [-73.958, 40.8003],
                        [-73.9498, 40.7968],
                        [-73.9737, 40.7648],
                        [-73.958, 40.8003],
                    ]
                ],
            ],
        }
    }


def test_compile_geojson_geometry_collection(context):
    geo = {
        "type": "GeometryCollection",
        "geometries": [
            {
                "type": "MultiPoint",
                "coordinates": [
                    [-73.9580, 40.8003],
                    [-73.9498, 40.7968],
                    [-73.9737, 40.7648],
                    [-73.9814, 40.7681],
                ],
            },
            {
                "type": "MultiLineString",
                "coordinates": [
                    [[-73.96943, 40.78519], [-73.96082, 40.78095]],
                    [[-73.96415, 40.79229], [-73.95544, 40.78854]],
                    [[-73.97162, 40.78205], [-73.96374, 40.77715]],
                    [[-73.97880, 40.77247], [-73.97036, 40.76811]],
                ],
            },
        ],
    }
    expr = compile_geo(geo, context=context)
    assert expr == {
        "$geometry": {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "MultiPoint",
                    "coordinates": [
                        [-73.9580, 40.8003],
                        [-73.9498, 40.7968],
                        [-73.9737, 40.7648],
                        [-73.9814, 40.7681],
                    ],
                },
                {
                    "type": "MultiLineString",
                    "coordinates": [
                        [[-73.96943, 40.78519], [-73.96082, 40.78095]],
                        [[-73.96415, 40.79229], [-73.95544, 40.78854]],
                        [[-73.97162, 40.78205], [-73.96374, 40.77715]],
                        [[-73.97880, 40.77247], [-73.97036, 40.76811]],
                    ],
                },
            ],
        }
    }
