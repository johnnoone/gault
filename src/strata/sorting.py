from __future__ import annotations

from typing import Any

from .types import AsRef, Context, Direction

type SortType = dict[str, Direction] | str | list[str | SortToken] | SortToken
type SortToken = str | tuple[AsRef, Direction]


class Sortable:
    pass


def normalize_sort(data: SortType, /, *, context: Context) -> dict[str, Any]:
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
            case AsRef() as alias:
                key, val = (alias.compile_field(context=context), 1)
            case (AsRef() as alias, direction):
                key, val = (alias.compile_field(context=context), direction)
            case (str() as key, direction):
                _, val = (key, direction)

        result[key] = val
    return result
