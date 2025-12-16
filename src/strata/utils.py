from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import MISSING
from typing import Any


def drop_missing[T: Mapping](mapping: T) -> T:
    return {key: val for key, val in mapping.items() if val is not MISSING}


def coerce_missing[T](x: Any, y: T) -> T:
    if x is MISSING:
        return y
    return x


async def to_list[T: Any](iterator: AsyncIterator[T]) -> list[T]:
    return [instance async for instance in iterator]


def nullfree_dict[T: dict](mapping: T) -> T:
    return {key: val for key, val in mapping.items() if val is not None}


def nullfree_list[T: list](sequence: T) -> T:
    return [element for element in sequence if element is not None]


def unwrap_array[T](elements: Sequence[T, Sequence[T]]) -> list[T]:
    if len(elements) == 1 and isinstance(elements[0], list | tuple):
        return list(elements[0])
    return list(elements)
