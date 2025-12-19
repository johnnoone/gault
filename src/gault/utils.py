from __future__ import annotations

from dataclasses import _MISSING_TYPE, MISSING
from typing import TYPE_CHECKING, Any, TypeVar, overload

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Sequence

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


def drop_missing(mapping: dict[K, V | _MISSING_TYPE]) -> dict[K, V]:
    return {key: val for key, val in mapping.items() if val is not MISSING}


async def to_list(iterator: AsyncIterator[T]) -> list[T]:
    return [instance async for instance in iterator]


def nullfree_dict(mapping: dict[K, V | None], /) -> dict[K, V]:
    return {key: val for key, val in mapping.items() if val is not None}


def nullfree_list(sequence: Sequence[T | None]) -> Sequence[T]:
    return [element for element in sequence if element is not None]


@overload
def unwrap_array(elements: tuple[Sequence[T]]) -> list[T]: ...


@overload
def unwrap_array(elements: tuple[T, ...]) -> list[T]: ...


def unwrap_array(elements: Any) -> list[T]:
    if len(elements) == 1 and isinstance(elements[0], list | tuple):
        return list(elements[0])
    return list(elements)
