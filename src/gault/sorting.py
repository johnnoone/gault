from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeAlias, assert_never, cast

from .types import AsRef

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from .types import Context

    Direction: TypeAlias = Literal[-1, 1] | Mapping[str, Any]
    Sort: TypeAlias = Mapping[str, Direction]
    SortParam: TypeAlias = tuple[str, Direction]
    SortValue: TypeAlias = int | str | Direction | None
    SortField: TypeAlias = AsRef | str
    SortToken: TypeAlias = SortField | tuple[SortField, SortValue]
    SortPayload: TypeAlias = SortToken | list[SortToken] | Mapping[SortField, SortValue]


def normalize_sort(obj: SortPayload | None, *, context: Context) -> Sort | None:
    token: SortToken
    normalized: list[SortParam] = []
    match obj:
        case str(tokens) if obj:
            for token in tokens.split(","):
                normalized += normalize_token(token, context=context)
        case tuple(token):
            normalized += normalize_token(token, context=context)
        case list(tokens):
            for token in tokens:
                normalized += normalize_token(token, context=context)
        case dict(tokens):
            for token in tokens.items():
                normalized += normalize_token(token, context=context)
        case _:
            normalized += normalize_token(cast("Any", obj), context=context)
    return dict(normalized) if normalized else None


def normalize_token(obj: SortToken, *, context: Context) -> Iterator[SortParam]:
    if False:
        yield

    match obj:
        case str(obj) if obj.startswith("-"):
            yield (obj[1:], -1)
        case str(obj) if obj:
            yield (obj, 1)
        case AsRef() as ref:
            yield (ref.compile_field(context=context), 1)
        case tuple([AsRef() as ref, _ as direction]):
            yield (ref.compile_field(context=context), direction or 1)
        case tuple([str() as key, _ as direction]):
            yield (key, direction or 1)
        case _:
            assert_never(obj)  # ty:ignore[type-assertion-failure]
