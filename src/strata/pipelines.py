from __future__ import annotations

from dataclasses import MISSING, dataclass, field, replace
from typing import TYPE_CHECKING, Any, Concatenate, Literal, Self

from .mappers import get_mapper
from .models import Attribute, Model, Schema, get_collection
from .operators import Operator
from .types import Path, PositiveInteger, RawField, RawPath
from .utils import coerce_missing, drop_missing

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import ParamSpec, TypeVar

    from .accumulators import Accumulator
    from .types import Document

    T = TypeVar("T")
    P = ParamSpec("P")

type Stage = dict[str, Any]


@dataclass
class Pipeline:
    stages: list[Stage] = field(default_factory=list, kw_only=True)

    def pipe(
        self,
        _0: Callable[Concatenate[Pipeline, P], T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        """Offers a structured way to apply a sequence of user-defined functions.

        Parameters
        ----------
        function
            Callable; will receive the frame as the first parameter,
            followed by any given args/kwargs.
        *args
            Arguments to pass to the UDF.
        **kwargs
            Keyword arguments to pass to the UDF.

        """
        return _0(self, **kwargs)

    def match(self, query: dict | Operator, /) -> Self:
        """Filter documents matching the specified condition(s)."""
        match query:
            case Operator():
                stage = {"$match": query.compile()}
            case _:
                stage = {"$match": query}
        return self.raw(stage)

    def skip(self, size: PositiveInteger, /) -> Self:
        """Skip the first n documents."""
        stage = {"$skip": size}
        return self.raw(stage)

    def take(self, size: PositiveInteger, /) -> Self:
        """Limit the number of documents passed to the next stage."""
        stage = {"$limit": size}
        return self.raw(stage)

    def sample(self, size: PositiveInteger, /) -> Self:
        """Randomly select the specified number of documents."""
        stage = {"$sample": {"size": size}}
        return self.raw(stage)

    def sort(self, spec: SortType, /) -> Self:
        """Reorder documents by the specified sort key."""
        spec = normalize_sort(spec)
        stage = {"$sort": spec}
        return self.raw(stage)

    def project(self, model: type[Schema | Model], /) -> Self:
        """Reshape documents by including, excluding, or adding fields."""
        match model:
            case dict():
                projection = model
            case _:
                projection = dict.fromkeys(get_mapper(model).db_fields, True)

        if projection:
            stage = {"$project": {"_id": False} | projection}
            return self.raw(stage)
        return self

    def bucket[T](
        self,
        by: AnyPath,
        /,
        boundaries: list[T],
        default: str = MISSING,
        output: dict[str, Accumulator] = MISSING,
    ) -> Self:
        """Categorize documents into buckets based on specified boundaries."""
        by = into_path(by)

        output = coerce_missing(output, {})

        stage = {
            "$bucket": drop_missing(
                {
                    "groupBy": by,
                    "boundaries": boundaries,
                    "default": default,
                    "output": {key: val.compile() for key, val in output.items()},
                },
            ),
        }
        return self.raw(stage)

    def bucket_auto(
        self,
        by: AnyPath,
        /,
        buckets: int,
        output: dict[str, Accumulator] = MISSING,
        granularity: Literal[
            "R5",
            "R10",
            "R20",
            "R40",
            "R80",
            "1-2-5",
            "E6",
            "E12",
            "E24",
            "E48",
            "E96",
            "E192",
            "POWERSOF2",
        ] = MISSING,
    ) -> Self:
        """Automatically categorize documents into a specified number of buckets."""
        by = into_path(by)

        output = coerce_missing(output, {})

        stage = {
            "$bucketAuto": drop_missing(
                {
                    "groupBy": by,
                    "buckets": buckets,
                    "output": {key: val.compile() for key, val in output.items()},
                    "granularity": granularity,
                },
            ),
        }
        return self.raw(stage)

    def group(
        self,
        by: AnyPath,
        /,
        accumulators: dict[str, Accumulator] = MISSING,
    ) -> Self:
        """Group documents by a specified expression and apply accumulators."""
        by = into_path(by)

        accumulators = coerce_missing(accumulators, {})

        def maybe_compile(obj: Any) -> dict:
            if isinstance(obj, dict):
                return obj
            return obj.compile()

        stage = {
            "$group": {
                "_id": by,
            }
            | {key: maybe_compile(val) for key, val in accumulators.items()},
        }
        return self.raw(stage)

    def set_field(self, field: field | str, value: Any, /) -> Self:
        """Add a new field or replace existing field value."""
        return self.set({field: value})

    def set(self, fields: dict[str, Any], /) -> Self:
        """Add new fields or replace existing field values."""
        stage = {"$set": dict(fields.items())}
        return self.raw(stage)

    def unset(self, *fields: AnyField) -> Self:
        """Remove specified fields from documents."""
        if fields:
            stage = {"$unset": [into_field(field) for field in fields]}
            return self.raw(stage)
        return self

    def unwind(
        self,
        field: AnyField,
        /,
        *,
        include_array_index: str = MISSING,
        preserve_null_and_empty_arrays: bool = False,
    ) -> Self:
        """Deconstruct an array field to output a document for each element."""
        stage = {
            "$unwind": drop_missing(
                {
                    "path": into_path(field),
                    "includeArrayIndex": include_array_index,
                    "preserveNullAndEmptyArrays": preserve_null_and_empty_arrays,
                },
            ),
        }
        return self.raw(stage)

    def count(self, output: AnyField, /) -> Self:
        """Return a count of the number of documents at this stage."""
        output = into_field(output)
        stage = {"$count": output}
        return self.raw(stage)

    def replace_with(self, expr: Any, /) -> Self:
        """Replace the input document with the specified document."""
        stage = {"$replaceWith": expr}
        return self.raw(stage)

    def union_with(
        self,
        other: CollectionPipeline | type[Schema | Model],
        /,
    ) -> Self:
        """Perform a union of two collections."""
        if isinstance(other, CollectionPipeline):
            body = {
                "coll": other.collection,
                "pipeline": other.build(),
            }
        elif issubclass(other, Schema | Model):
            body = {
                "coll": get_collection(other),
                "pipeline": Pipeline().project(other).build(),
            }
        else:
            raise NotImplementedError

        stage = {"$unionWith": body}
        return self.raw(stage)

    def graph_lookup(
        self,
        other: type[Schema | Model],
        /,
        start_with: AnyPath,
        local_field: AnyField,
        foreign_field: AnyField,
        into: AnyField,
        max_depth: int = MISSING,
        depth_field: AnyField | None = MISSING,
        restrict_search_with_match: int = MISSING,
    ) -> Self:
        """Perform a recursive search on a collection."""
        local_field = into_field(local_field)
        foreign_field = into_field(foreign_field)
        depth_field = into_field(depth_field)

        stage = {
            "$graphLookup": drop_missing(
                {
                    "from": get_collection(other),
                    "startWith": into_path(start_with),
                    "connectFromField": local_field,
                    "connectToField": foreign_field,
                    "as": into_field(into),
                    "maxDepth": max_depth,
                    "depthField": depth_field,
                    "restrictSearchWithMatch": restrict_search_with_match,
                },
            ),
        }
        return self.raw(stage)

    def lookup(
        self,
        other: CollectionPipeline | DocumentsPipeline | type[Schema | Model],
        /,
        *,
        local_field: Path = MISSING,
        foreign_field: Path = MISSING,
        into: AnyField,
    ) -> Self:
        """Perform a left outer join to another collection."""
        if isinstance(other, CollectionPipeline):
            body = drop_missing(
                {
                    "from": other.collection,
                    "localField": local_field.value,
                    "foreignField": foreign_field.value,
                    "pipeline": other.build(),
                    "as": into_field(into),
                },
            )
        elif isinstance(other, DocumentsPipeline):
            body = drop_missing(
                {
                    "localField": local_field.value,
                    "foreignField": foreign_field.value,
                    "pipeline": other.build(),
                    "as": into_field(into),
                },
            )
        elif isinstance(other, Schema | Model):
            body = drop_missing(
                {
                    "from": get_collection(other),
                    "localField": local_field.value,
                    "foreignField": foreign_field.value,
                    "pipeline": Pipeline().project(other).build(),
                    "as": into_field(into),
                },
            )
        else:
            raise NotImplementedError
        stage = {"$lookup": body}
        return self.raw(stage)

    def facet(self, output: dict[str, Pipeline], /) -> Self:
        """Process multiple pipelines within a single stage on the same input."""
        if output:
            body = {key: val.build() for key, val in output.items()}
            stage = {"$facet": body}
            return self.raw(stage)
        return self

    def raw(self, stage: Stage, /) -> Self:
        return replace(self, stages=[*self.stages, stage])

    def build(self) -> list[Stage]:
        return list(self.stages)

    @classmethod
    def documents(cls, documents: list[Document]) -> DocumentsPipeline:
        return DocumentsPipeline(documents)


@dataclass
class CollectionPipeline(Pipeline):
    collection: str


@dataclass
class DocumentsPipeline(Pipeline):
    documents: list[Document]

    def build(self) -> list[Stage]:
        stage = {"$documents": self.documents}
        return [stage, *super().build()]


type AnyPath = Path | RawPath
type AnyField = Path | str


def into_path(expr: AnyPath | None) -> RawPath | None:
    if expr is None:
        return None
    if isinstance(expr, Path):
        return "$" + expr.value
    if expr.startswith("$"):
        return expr
    msg = "Expression must start with $"
    raise ValueError(msg)


def into_field(expr: AnyField | None) -> RawField | None:
    if expr is MISSING:
        return MISSING
    if expr is None:
        return None
    if isinstance(expr, Path):
        return expr.value
    if not expr.startswith("$"):
        return expr
    msg = "Expression must not start with $"
    raise ValueError(msg)


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
            case Attribute(db_alias=db_alias):
                key, val = (db_alias, 1)
            case (Attribute(db_alias=db_alias), direction):
                key, val = (db_alias, direction)
            case (str() as key, direction):
                _, val = (key, direction)

        result[key] = val
    return result
