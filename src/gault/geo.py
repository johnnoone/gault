from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, TypeAlias

if TYPE_CHECKING:
    from .types import Context, MongoExpression

    Geo: TypeAlias = "Box" | "Center" | "CenterSphere" | "GeoJSON"


def compile_geo(value: Geo | MongoExpression, *, context: Context) -> Any:
    match value:
        case {"$box": _} | {"$center": _} | {"$centerSphere": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/box/
            # https://www.mongodb.com/docs/manual/reference/operator/query/center/
            # https://www.mongodb.com/docs/manual/reference/operator/query/centerSphere/
            return value
        case {"$geometry": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/geometry/
            return value
        case {
            "type": "Point"
            | "LineString"
            | "Polygon"
            | "MultiPoint"
            | "MultiLineString"
            | "MultiPolygon"
            | "GeometryCollection"
        }:
            return {"$geometry": value}
        case GeoJSON():
            return value.compile_expression(context=context)
        case Box() | Center() | CenterSphere():
            return value.compile_expression(context=context)
        case _:
            raise NotImplementedError


class GeoJSON(ABC):
    @abstractmethod
    def compile_expression(self, *, context: Context) -> MongoExpression: ...

    @abstractmethod
    def get_coordinates(self) -> Any: ...


@dataclass
class Point(GeoJSON):
    x: float
    y: float

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "Point",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return compile_position(self)


@dataclass
class LineString(GeoJSON):
    points: list[Point]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "LineString",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [point.get_coordinates() for point in self.points]


@dataclass
class Polygon(GeoJSON):
    line_strings: list[LineString]
    crs: Literal["urn:x-mongodb:crs:strictwinding:EPSG:4326"] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression:
        if name := self.crs:
            custom = {
                "crs": {
                    "type": "name",
                    "properties": {"name": name},
                },
            }
        else:
            custom = {}
        return {
            "$geometry": {
                "type": "Polygon",
                "coordinates": self.get_coordinates(),
            }
            | custom
        }

    def get_coordinates(self) -> Any:
        return [line_string.get_coordinates() for line_string in self.line_strings]


@dataclass
class MultiPoint(GeoJSON):
    points: list[Point]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "MultiPoint",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [point.get_coordinates() for point in self.points]


@dataclass
class MultiLineString(GeoJSON):
    line_strings: list[LineString]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "MultiLineString",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [line_string.get_coordinates() for line_string in self.line_strings]


@dataclass
class MultiPolygon(GeoJSON):
    polygons: list[Polygon]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "MultiPolygon",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [polygon.get_coordinates() for polygon in self.polygons]


@dataclass
class GeometryCollection(GeoJSON):
    geometries: list[GeoJSON]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "GeometryCollection",
                "geometries": [
                    geometry.compile_expression(context=context)["$geometry"]  # type: ignore[call-overload, index]
                    for geometry in self.geometries
                ],
            }
        }

    def get_coordinates(self) -> Any:
        return [geometry.get_coordinates() for geometry in self.geometries]


@dataclass
class Box:
    bottom_left_coordinates: Point
    upper_right_coordinates: Point

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$box": [
                compile_position(self.bottom_left_coordinates),
                compile_position(self.upper_right_coordinates),
            ],
        }


@dataclass
class Center:
    coordinates: Point
    radius: float

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$center": [
                compile_position(self.coordinates),
                self.radius,
            ],
        }


@dataclass
class CenterSphere:
    coordinates: Point
    radius: float

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$centerSphere": [
                compile_position(self.coordinates),
                self.radius,
            ],
        }


class Coordinates(NamedTuple):
    x: float
    y: float


def compile_position(input: Coordinates | Point, /) -> list[float]:
    match input:
        case Coordinates(x, y):
            return [x, y]
        case Point(x, y):
            return [x, y]
        case _:
            raise NotImplementedError
