from collections.abc import AsyncIterator, Mapping
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
