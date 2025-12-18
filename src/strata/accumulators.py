from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .types import AsRef
from .types import AsAlias, Context

type Expr = Any


class Accumulator(ABC, AsAlias):
    @abstractmethod
    def compile(self, *, context: Context) -> Any: ...


@dataclass
class AddToSet(Accumulator):
    """Returns an array of unique expression values for each group."""

    expr: Expr

    def compile(self, *, context: Context) -> Any:
        return {"$addToSet": compile_accumulator(self.expr, context=context)}


@dataclass
class Avg(Accumulator):
    """Returns the average of numeric values."""

    expr: Expr

    def compile(self, *, context: Context) -> Any:
        return {"$avg": compile_accumulator(self.expr, context=context)}


@dataclass
class Bottom(Accumulator):
    """Returns the bottom element within a group according to the specified sort order."""

    sort_by: Any
    output: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$bottom": {
                "sortBy": compile_accumulator(self.sort_by, context=context),
                "output": compile_accumulator(self.output, context=context),
            },
        }


@dataclass
class BottomN(Accumulator):
    """Returns an aggregation of the bottom n elements within a group, according to the specified sort order."""

    n: Expr
    sort_by: Any
    output: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$bottomN": {
                "n": compile_accumulator(self.n, context=context),
                "sortBy": compile_accumulator(self.sort_by, context=context),
                "output": compile_accumulator(self.output, context=context),
            },
        }


@dataclass
class Count(Accumulator):
    """Returns the number of documents in a group."""

    def compile(self, *, context: Context) -> Any:
        return {"$count": {}}


@dataclass
class First(Accumulator):
    """Returns the value that results from applying an expression to the first document in a group."""

    value: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$first": compile_accumulator(self.value, context=context),
        }


@dataclass
class FirstN(Accumulator):
    """Returns an aggregation of the first n elements within a group."""

    value: Expr
    n: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$firstN": {
                "input": compile_accumulator(self.value, context=context),
                "n": compile_accumulator(self.n, context=context),
            },
        }


@dataclass
class Last(Accumulator):
    """Returns the value that results from applying an expression to the last document in a group."""

    value: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$last": compile_accumulator(self.value, context=context),
        }


@dataclass
class LastN(Accumulator):
    """Returns an aggregation of the last n elements within a group."""

    value: Expr
    n: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$lastN": {
                "input": compile_accumulator(self.value, context=context),
                "n": compile_accumulator(self.n, context=context),
            },
        }


@dataclass
class Max(Accumulator):
    """Returns the maximum value."""

    value: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$max": compile_accumulator(self.value, context=context),
        }


@dataclass
class MaxN(Accumulator):
    """Returns an aggregation of the n maximum valued elements within a group."""

    value: Expr
    n: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$maxN": {
                "input": compile_accumulator(self.value, context=context),
                "n": compile_accumulator(self.n, context=context),
            },
        }


@dataclass
class Median(Accumulator):
    """Returns an approximation of the median value."""

    input: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$median": {
                "input": compile_accumulator(self.input, context=context),
                "method": "approximate",
            },
        }


@dataclass
class MergeObjects(Accumulator):
    """Combines multiple documents into a single document."""

    objects: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$mergeObjects": compile_accumulator(self.objects, context=context),
        }


@dataclass
class Min(Accumulator):
    """Returns the minimum value."""

    value: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$min": compile_accumulator(self.value, context=context),
        }


@dataclass
class MinN(Accumulator):
    """Returns an aggregation of the n minimum valued elements within a group."""

    value: Expr
    n: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$minN": {
                "input": compile_accumulator(self.value, context=context),
                "n": compile_accumulator(self.n, context=context),
            },
        }


@dataclass
class Percentile(Accumulator):
    """Returns an approximation of a percentile value."""

    input: Expr
    p: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$percentile": {
                "input": compile_accumulator(self.input, context=context),
                "p": compile_accumulator(self.p, context=context),
                "method": "approximate",
            },
        }


@dataclass
class Push(Accumulator):
    """Returns an array of expression values for documents in each group."""

    value: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$push": compile_accumulator(self.value, context=context),
        }


@dataclass
class StdDevPop(Accumulator):
    """Returns the population standard deviation of the input values."""

    value: Expr
    p: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$stdDevPop": compile_accumulator(self.value, context=context),
        }


@dataclass
class StdDevSamp(Accumulator):
    """Returns the sample standard deviation of the input values."""

    value: Expr
    p: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$stdDevSamp": compile_accumulator(self.value, context=context),
        }


@dataclass
class Sum(Accumulator):
    """Returns the sum of numeric values."""

    value: Expr

    def compile(self, *, context: Context) -> Any:
        return {"$sum": compile_accumulator(self.value, context=context)}


@dataclass
class Top(Accumulator):
    """Returns the top element within a group according to the specified sort order."""

    sort_by: Any
    output: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$top": {
                "sortBy": compile_accumulator(self.sort_by, context=context),
                "output": compile_accumulator(self.output, context=context),
            },
        }


@dataclass
class TopN(Accumulator):
    """Returns an aggregation of the top n elements within a group, according to the specified sort order."""

    n: Expr
    sort_by: Any
    output: Expr

    def compile(self, *, context: Context) -> Any:
        return {
            "$topN": {
                "n": compile_accumulator(self.n, context=context),
                "sortBy": compile_accumulator(self.sort_by, context=context),
                "output": compile_accumulator(self.output, context=context),
            },
        }


def compile_accumulator(obj: Any, *, context: Context) -> Any:
    if isinstance(obj, Accumulator):
        return obj.compile(context=context)
    if isinstance(obj, AsRef):
        return obj.compile_expression(context=context)
    return obj
