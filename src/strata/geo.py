from __future__ import annotations

from typing import Any

type Geometry = Point | Polygon | MultiPolygon


class Point:
    lon: float
    lat: float

    def compile(self) -> Any:
        return {
            "type": "Point",
            "coordinates": [self.lon, self.lat],
        }


class LineString:
    coordinates: list[Point]

    def compile(self) -> Any:
        return {
            "type": "LineString",
            "coordinates": [[point.lon, point.lat] for point in self.coordinates],
        }


class Polygon:
    lines: list[LineString[Point]]

    crs: str | None = None

    def compile(self) -> Any:
        data = {
            "type": "Polygon",
            "coordinates": [
                [[point.lon, point.lat] for point in line.coordinates]
                for line in self.lines
            ],
        }
        if crs := self.crs:
            data["crs"] = {
                "type": crs,
                "properties": {
                    "name": "urn:x-mongodb:crs:strictwinding:EPSG:4326",
                },
            }

        return data


class MultiPolygon:
    polygons: list[Polygon]

    crs: str | None = None

    def compile(self) -> Any:
        data = {
            "type": "MultiPolygon",
            "coordinates": [
                polygon.compile()["coordinates"] for polygon in self.polygons
            ],
        }
        if crs := self.crs:
            data["crs"] = {
                "type": crs,
                "properties": {
                    "name": "urn:x-mongodb:crs:strictwinding:EPSG:4326",
                },
            }

        return data


class MultiPoint:
    coordinates: list[Point]

    def compile(self) -> Any:
        return {
            "type": "MultiPoint",
            "coordinates": [[point.lon, point.lat] for point in self.coordinates],
        }


class MultiLineString:
    lines: list[LineString[Point]]

    def compile(self) -> Any:
        return {
            "type": "MultiLineString",
            "coordinates": [
                [[point.lon, point.lat] for point in line.coordinates]
                for line in self.lines
            ],
        }


class Box:
    point1: Point
    point2: Point

    def compile(self) -> Any:
        return {
            "$box": [
                [self.point1.lon, self.point1.lat],
                [self.point2.lon, self.point2.lat],
            ],
        }


class Center:
    lon: Point
    lat: Point
    radius: float

    def compile(self) -> Any:
        return {
            "$center": [
                [self.point1.lon, self.point1.lat],
                self.radius,
            ],
        }


class CenterSphere:
    lon: Point
    lat: Point
    radius: float

    def compile(self) -> Any:
        return {
            "$centerSphere": [
                [self.point1.lon, self.point1.lat],
                self.radius,
            ],
        }
