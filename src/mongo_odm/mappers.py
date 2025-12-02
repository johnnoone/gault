from __future__ import annotations

from dataclasses import MISSING, fields
from functools import cached_property
from typing import TYPE_CHECKING, Any, NamedTuple, cast
from weakref import WeakKeyDictionary

from .models import unwrap_model
from .utils import drop_missing

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .models import FieldMetadata, Model, Projection
    from .types import Document


MAPPERS: dict[type[Model], Mapper] = WeakKeyDictionary()


def get_mapper[M: Model | Projection](model: M | type[M]) -> Mapper[M]:
    model = unwrap_model(model)
    if mapper := MAPPERS.get(model):
        return mapper
    mapper = MAPPERS[model] = Mapper(model)
    return mapper


class Corres(NamedTuple):
    model_field: str
    db_field: str
    pk: bool


class CoinCoin(NamedTuple):
    model_field: str
    db_field: str
    value: Any
    pk: bool


class Mapper[M: Model | Projection]:
    def __init__(self, model: type[M]) -> None:
        self.model = model

    @cached_property
    def field_mapping(self) -> list[Corres]:
        result = []
        for field in fields(self.model):
            model_field = field.name
            metadata = cast("FieldMetadata", field.metadata)
            db_field = metadata.get("db_alias")
            pk = metadata.get("pk") or False
            result.append(Corres(model_field, db_field or model_field, pk=pk))
        return result

    @cached_property
    def db_fields(self) -> set[str]:
        return {corres.db_field for corres in self.field_mapping}

    def map(self, document: Document) -> M:
        attrs = {}
        for corres in self.field_mapping:
            attrs[corres.model_field] = document.get(corres.db_field, MISSING)
            attrs = drop_missing(attrs)
        return self.model(**attrs)

    def to_document(self, instance: M) -> Document:
        return {
            corres.db_field: corres.value for corres in self.iter_document(instance)
        }

    def to_filter(self, instance: M) -> Document:
        return {
            corres.db_field: corres.value
            for corres in self.iter_document(instance)
            if corres.pk is True
        }

    def iter_document(self, instance: M) -> Iterator[CoinCoin]:
        for corres in self.field_mapping:
            yield CoinCoin(
                corres.model_field,
                corres.db_field,
                getattr(instance, corres.model_field),
                corres.pk,
            )
