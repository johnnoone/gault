from __future__ import annotations

from dataclasses import MISSING, fields
from functools import cached_property
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar, cast, no_type_check

from .models import unwrap_model

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .models import AttributeMetadata, Model
    from .types import Document

M = TypeVar("M", bound="Model")

MAPPERS: dict[type[Model], Mapper[Model]] = {}


@no_type_check
def get_mapper(model: M | type[M]) -> Mapper[M]:
    model = unwrap_model(model)
    if mapper := MAPPERS.get(model):
        return mapper
    mapper = MAPPERS[model] = Mapper(model)
    return mapper


class FieldMapping(NamedTuple):
    model_field: str
    db_field: str
    pk: bool


class FieldEntry(NamedTuple):
    model_field: str
    db_field: str
    value: Any
    pk: bool


class Mapper(Generic[M]):
    def __init__(self, model: type[M]) -> None:
        self.model = model

    @cached_property
    def field_mapping(self) -> list[FieldMapping]:
        result = []
        for field in fields(self.model):  # type: ignore[arg-type]
            model_field = field.name
            metadata = cast("AttributeMetadata", field.metadata)
            db_field = metadata.get("db_alias")
            pk = metadata.get("pk") or False
            result.append(FieldMapping(model_field, db_field or model_field, pk=pk))
        return result

    @cached_property
    def db_fields(self) -> set[str]:
        return {corres.db_field for corres in self.field_mapping}

    def map(self, document: Document) -> M:
        attrs = {}
        for corres in self.field_mapping:
            value = document.get(corres.db_field, MISSING)
            if value is not MISSING:
                attrs[corres.model_field] = value
        return self.model(**attrs)

    def to_document(self, instance: M) -> Document:
        return {
            corres.db_field: corres.value for corres in self.iter_document(instance)
        }

    def to_filter(self, instance: M) -> Document:
        return {
            corres.db_field: getattr(instance, corres.model_field)
            for corres in self.field_mapping
            if corres.pk
        }

    def iter_document(self, instance: M) -> Iterator[FieldEntry]:
        for corres in self.field_mapping:
            yield FieldEntry(
                corres.model_field,
                corres.db_field,
                getattr(instance, corres.model_field),
                corres.pk,
            )
