from __future__ import annotations

from typing import Any

from .types import DBAlias
from .types import Direction

type SortType = dict[str, Direction] | str | list[str | SortToken] | SortToken
type SortToken = str | tuple[Sortable, Direction]


class Sortable:
    pass


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
            case DBAlias() as alias:
                key, val = (alias.get_db_alias(), 1)
            case (DBAlias() as alias, direction):
                key, val = (alias.get_db_alias(), direction)
            case (str() as key, direction):
                _, val = (key, direction)

        result[key] = val
    return result
