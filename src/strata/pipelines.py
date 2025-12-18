from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, field, replace
from typing import TYPE_CHECKING, Any, Concatenate, Literal, Self, overload

from .accumulators import compile_accumulator
from .compilers import compile_expression, compile_field, compile_path, compile_query
from .mappers import get_mapper
from .models import Model, Schema, get_collection
from .operators import Operator
from .sorting import SortType, normalize_sort
from .utils import drop_missing, nullfree_dict, unwrap_array

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from typing import ParamSpec, TypeVar

    from .accumulators import Accumulator
    from .predicates import Field, Predicate
    from .types import (
        Aliased,
        Context,
        Document,
        MongoExpression,
        PositiveInteger,
    )

    T = TypeVar("T")
    P = ParamSpec("P")


type Stage = dict[str, Any]


@dataclass
class Pipeline:
    steps: list[Step] = field(default_factory=list, kw_only=True)

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
        step = MatchStep(query=query)
        return self.raw(step)

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
        step = ProjectStep(model)
        return self.raw(step)

    def bucket[T](
        self,
        by: str | Field,
        /,
        boundaries: list[T],
        default: str = MISSING,
        output: dict[str, Accumulator] = MISSING,
    ) -> Self:
        """Categorize documents into buckets based on specified boundaries."""
        step = BucketStep(
            by=by,
            boundaries=boundaries,
            default=default,
            output=output,
        )
        return self.raw(step)

    def bucket_auto(
        self,
        by: str | Field,
        /,
        buckets: int,
        output: dict[str, Accumulator] | None = None,
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
        ]
        | None = None,
    ) -> Self:
        """Automatically categorize documents into a specified number of buckets."""
        step = BucketAutoStep(
            by=by,
            buckets=buckets,
            output=output,
            granularity=granularity,
        )
        return self.raw(step)

    @overload
    def group(
        self, accumulators: dict[str, Accumulator], *, by: MongoExpression
    ) -> Self: ...

    @overload
    def group(
        self, *accumulators: Aliased[Accumulator], by: MongoExpression
    ) -> Self: ...

    def group(self, *accumulators: Any, by: MongoExpression = None) -> Self:
        """Group documents by a specified expression and apply accumulators."""
        if accumulators and isinstance(accumulators[0], dict):
            mapping: dict[str, Accumulator] = accumulators[0]
        else:
            mapping = {
                aliased.ref: aliased.value for aliased in unwrap_array(accumulators)
            }
        step = GroupStep(by=by, accumulators=mapping)
        return self.raw(step)

    def set_field(self, field: Field | str, value: Any, /) -> Self:
        """Add a new field or replace existing field value."""
        return self.set({field: value})

    def set(self, fields: dict[str, MongoExpression], /) -> Self:
        """Add new fields or replace existing field values."""
        step = SetStep(fields=fields)
        return self.raw(step)

    def unset(self, *fields: Field | str) -> Self:
        """Remove specified fields from documents."""
        step = UnsetStep(fields=list(fields))
        return self.raw(step)

    def unwind(
        self,
        field: Field | str,
        /,
        *,
        include_array_index: str | None = None,
        preserve_null_and_empty_arrays: bool | None = None,
    ) -> Self:
        """Deconstruct an array field to output a document for each element."""
        step = UnwindStep(
            field=field,
            include_array_index=include_array_index,
            preserve_null_and_empty_arrays=preserve_null_and_empty_arrays,
        )
        return self.raw(step)

    def count(self, output: Field | str, /) -> Self:
        """Return a count of the number of documents at this stage."""
        step = CountStep(output)
        return self.raw(step)

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
        start_with: str | Field,
        local_field: str | Field,
        foreign_field: str | Field,
        into: str | Field,
        max_depth: int | None = None,
        depth_field: str | Field | None = None,
        restrict_search_with_match: MongoExpression | None = None,
    ) -> Self:
        """Perform a recursive search on a collection."""
        step = GraphLookupStep(
            collection=get_collection(other),
            into=into,
            start_with=start_with,
            connect_from_field=local_field,
            connect_to_field=foreign_field,
            max_depth=max_depth,
            depth_field=depth_field,
            restrict_search_with_match=restrict_search_with_match,
        )
        return self.raw(step)

    def lookup(
        self,
        other: CollectionPipeline | DocumentsPipeline | type[Schema | Model],
        /,
        *,
        local_field: str | Field | None = None,
        foreign_field: str | Field | None = None,
        into: str | Field,
    ) -> Self:
        """Perform a left outer join to another collection."""
        if isinstance(other, CollectionPipeline):
            collection = other.collection
            pipeline = other
        elif isinstance(other, DocumentsPipeline):
            collection = None
            pipeline = other
        elif other and issubclass(other, Schema | Model):
            collection = get_collection(other)
            pipeline = None
        else:
            raise NotImplementedError
        step = LookupStep(
            collection=collection,
            pipeline=pipeline,
            local_field=local_field,
            foreign_field=foreign_field,
            into=into,
        )

        return self.raw(step)

    @overload
    def facet(self, facets: dict[str, Pipeline], /) -> Self: ...

    @overload
    def facet(self, *facets: Aliased[Pipeline]) -> Self: ...

    def facet(self, *facets: Any) -> Self:
        """Process multiple pipelines within a single stage on the same input."""
        if facets and isinstance(facets[0], dict):
            mapping = facets[0]
        else:
            for aliased in unwrap_array(facets):
                mapping[aliased.ref] = aliased.value

        step = FacetStep(facets=mapping)
        return self.raw(step)

    def raw(self, stage: Step | Stage, /) -> Self:
        if not isinstance(stage, Step):
            stage = Raw(stage)
        return replace(self, steps=[*self.steps, stage])

    def build(self, *, context: Context | None = None) -> list[Stage]:
        context = context or {}
        stages = []
        for step in self.steps:
            stages += step.compile(context=context)
        return stages

    @classmethod
    def documents(cls, *documents: list[Document]) -> DocumentsPipeline:
        documents = unwrap_array(documents)
        return DocumentsPipeline(documents)


@dataclass
class CollectionPipeline(Pipeline):
    collection: str


@dataclass
class DocumentsPipeline(Pipeline):
    documents: list[Document]

    def build(self, *, context: Context | None = None) -> list[Stage]:
        context = context or {}
        stage = {"$documents": self.documents}
        return [stage, *super().build(context=context)]


class Step(ABC):
    @abstractmethod
    def compile(self, context: Context) -> Iterator[Stage]: ...


@dataclass
class Raw(Step):
    stage: dict

    def compile(self, context: Context) -> Iterator[Stage]:
        yield self.stage


@dataclass
class FacetStep(Step):
    facets: dict[str, Pipeline]

    def compile(self, context: Context) -> Iterator[Stage]:
        body = {key: val.build(context=context) for key, val in self.facets.items()}
        stage = {"$facet": body}
        yield stage


@dataclass
class MatchStep(Step):
    query: dict | Operator | Predicate

    def compile(self, context: Context) -> Iterator[Stage]:
        match self.query:
            case Operator():
                stage = {"$match": self.query.compile(context=context)}
            case _:
                stage = {"$match": compile_query(self.query, context=context)}
        yield stage


@dataclass
class GroupStep(Step):
    by: MongoExpression
    accumulators: dict[str, Accumulator]

    def compile(self, context: Context) -> Iterator[Stage]:
        def maybe_compile(obj: Any) -> dict:
            if isinstance(obj, dict):
                return obj
            return obj.compile(context=context)

        yield {
            "$group": {
                "_id": compile_expression(self.by, context=context),
            }
            | {
                compile_field(key, context=context): maybe_compile(val)
                for key, val in self.accumulators.items()
            },
        }


@dataclass
class LookupStep(Step):
    collection: str
    into: str | Field
    pipeline: Pipeline | None = None
    local_field: str | Field | None = None
    foreign_field: str | Field | None = None

    def compile(self, context: Context) -> Iterator[Stage]:
        pipeline = self.pipeline.build(context=context) if self.pipeline else None
        local_field = (
            compile_field(self.local_field, context=context)
            if self.local_field
            else None
        )
        foreign_field = (
            compile_field(self.foreign_field, context=context)
            if self.foreign_field
            else None
        )

        yield {
            "$lookup": nullfree_dict(
                {
                    "from": self.collection,
                    "localField": local_field,
                    "foreignField": foreign_field,
                    "pipeline": pipeline,
                    "as": self.into,
                }
            )
        }


@dataclass
class GraphLookupStep(Step):
    collection: str
    into: str | Field
    start_with: MongoExpression | list[MongoExpression]
    connect_from_field: str | Field | None = None
    connect_to_field: str | Field | None = None
    max_depth: int | None = None
    depth_field: str | Field | None = None
    restrict_search_with_match: MongoExpression | None = None

    def compile(self, context: Context) -> Iterator[Stage]:
        if self.depth_field:
            depth_field = compile_field(self.depth_field, context=context)
        else:
            depth_field = None

        if self.restrict_search_with_match:
            query = compile_query(self.restrict_search_with_match, context=context)
        else:
            query = None

        yield {
            "$graphLookup": nullfree_dict(
                {
                    "from": self.collection,
                    "startWith": compile_query(self.start_with, context=context),
                    "connectFromField": compile_field(
                        self.connect_from_field, context=context
                    ),
                    "connectToField": compile_field(
                        self.connect_to_field, context=context
                    ),
                    "as": compile_field(self.into, context=context),
                    "maxDepth": self.max_depth,
                    "depthField": depth_field,
                    "restrictSearchWithMatch": query,
                },
            ),
        }


@dataclass
class BucketStep[T](Step):
    by: Field | str
    boundaries: list[T]
    default: str
    output: dict[str, Accumulator]

    def compile(self, context: Context) -> Iterator[Stage]:
        yield {
            "$bucket": {
                "groupBy": compile_path(self.by, context=context),
                "boundaries": self.boundaries,
                "default": self.default,
                "output": {
                    key: compile_accumulator(val, context=context)
                    for key, val in self.output.items()
                },
            }
        }


@dataclass
class BucketAutoStep(Step):
    by: Field | str
    buckets: int
    output: dict[str, Accumulator] | None = None
    granularity: str | None = None

    def compile(self, context: Context) -> Iterator[Stage]:
        if self.output:
            output = {
                compile_field(key, context=context): compile_accumulator(
                    val, context=context
                )
                for key, val in self.output.items()
            }
        else:
            output = None

        yield {
            "$bucketAuto": nullfree_dict(
                {
                    "groupBy": compile_path(self.by, context=context),
                    "buckets": self.buckets,
                    "output": output,
                    "granularity": self.granularity,
                },
            ),
        }


@dataclass
class ProjectStep(Step):
    model: type[Schema | Model] | dict

    def compile(self, context: Context) -> Iterator[Stage]:
        match self.model:
            case dict():
                projection = self.model
            case _:
                projection = dict.fromkeys(get_mapper(self.model).db_fields, True)
        yield {"$project": {"_id": False} | projection}


@dataclass
class UnwindStep(Step):
    field: Field | str
    include_array_index: Field | str | None = None
    preserve_null_and_empty_arrays: bool | None = None

    def compile(self, context: Context) -> Iterator[Stage]:
        if self.include_array_index:
            include_array_index = compile_path(
                self.include_array_index, context=context
            )
        else:
            include_array_index = None

        yield {
            "$unwind": drop_missing(
                {
                    "path": compile_path(self.field, context=context),
                }
                | nullfree_dict(
                    {
                        "includeArrayIndex": include_array_index,
                        "preserveNullAndEmptyArrays": self.preserve_null_and_empty_arrays,
                    }
                ),
            ),
        }


@dataclass
class SetStep(Step):
    fields: dict[Field | str, MongoExpression]

    def compile(self, context: Context) -> Iterator[Stage]:
        yield {
            "$set": {
                compile_field(field, context=context): compile_expression(
                    expression, context=context
                )
                for field, expression in self.fields.items()
            }
        }


@dataclass
class UnsetStep(Step):
    fields: list[Field | str]

    def compile(self, context: Context) -> Iterator[Stage]:
        yield {
            "$unset": [compile_field(field, context=context) for field in self.fields]
        }


@dataclass
class CountStep(Step):
    output: Field | str

    def compile(self, context: Context) -> Iterator[Stage]:
        yield {
            "$count": compile_field(self.output, context=context),
        }
