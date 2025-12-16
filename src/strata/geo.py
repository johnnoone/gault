from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .types import Context

type Geo = Box | Center | CenterSphere | GeoJSON
type Box = Any
type Center = Any
type CenterSphere = Any
type GeoJSON = Any


def compile_geo(value: Geo, *, context: Context) -> Any:
    match value:
        case {"$box": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/box/
            return value
        case {"$center": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/center/
            return value
        case {"$centerSphere": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/centerSphere/
            return value
        case {"$geometry": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/geometry/
            return value
        case _:
            raise NotImplementedError
