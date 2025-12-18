from __future__ import annotations

from typing import Any

from strata.models import AttributeSpec

type SortType = dict[str, Any] | str | list[str | tuple[Any, Any]] | tuple[Any, Any]


def normalize_sort(data: SortType, /) -> dict[str, Any]:
    if isinstance(data, str):
        data = data.split(",")
    elif isinstance(data, tuple):
        data = [data]
    elif isinstance(data, dict):
        data = list(data.items())

    result = {}
    for item in data:
        match item:
            case str() if item.startswith("-"):
                key, val = (item[1:], -1)
            case str() if item:
                key, val = (item, 1)
            case AttributeSpec(db_alias=db_alias):
                key, val = (db_alias, 1)
            case (AttributeSpec(db_alias=db_alias), direction):
                key, val = (db_alias, direction)
            case (str() as key, direction):
                _, val = (key, direction)

        result[key] = val
    return result
