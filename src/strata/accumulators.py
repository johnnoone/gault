from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .types import Path

type Expr = Any


class Accumulator(ABC):
    @abstractmethod
    def compile(self) -> Any: ...


@dataclass
class AddToSet(Accumulator):
    """Returns an array of unique expression values for each group."""

    expr: Expr

    def compile(self) -> Any:
        return {"$addToSet": compile(self.expr)}


@dataclass
class Avg(Accumulator):
    """Returns the average of numeric values."""

    expr: Expr

    def compile(self) -> Any:
        return {"$avg": compile(self.expr)}


@dataclass
class Bottom(Accumulator):
    """Returns the bottom element within a group according to the specified sort order."""

    sort_by: Any
    output: Expr

    def compile(self) -> Any:
        return {
            "$bottom": {
                "sortBy": compile(self.sort_by),
                "output": compile(self.output),
            },
        }


@dataclass
class BottomN(Accumulator):
    """Returns an aggregation of the bottom n elements within a group, according to the specified sort order."""

    n: Expr
    sort_by: Any
    output: Expr

    def compile(self) -> Any:
        return {
            "$bottomN": {
                "n": compile(self.n),
                "sortBy": compile(self.sort_by),
                "output": compile(self.output),
            },
        }


@dataclass
class Count(Accumulator):
    """Returns the number of documents in a group."""

    def compile(self) -> Any:
        return {"$count": {}}


@dataclass
class First(Accumulator):
    """Returns the value that results from applying an expression to the first document in a group."""

    value: Expr

    def compile(self) -> Any:
        return {
            "$first": compile(self.value),
        }


@dataclass
class FirstN(Accumulator):
    """Returns an aggregation of the first n elements within a group."""

    value: Expr
    n: Expr

    def compile(self) -> Any:
        return {
            "$firstN": {
                "input": compile(self.value),
                "n": compile(self.n),
            },
        }


@dataclass
class Last(Accumulator):
    """Returns the value that results from applying an expression to the last document in a group."""

    value: Expr

    def compile(self) -> Any:
        return {
            "$last": compile(self.value),
        }


@dataclass
class LastN(Accumulator):
    """Returns an aggregation of the last n elements within a group."""

    value: Expr
    n: Expr

    def compile(self) -> Any:
        return {
            "$lastN": {
                "input": compile(self.value),
                "n": compile(self.n),
            },
        }


@dataclass
class Max(Accumulator):
    """Returns the maximum value."""

    value: Expr

    def compile(self) -> Any:
        return {
            "$max": compile(self.value),
        }


@dataclass
class MaxN(Accumulator):
    """Returns an aggregation of the n maximum valued elements within a group."""

    value: Expr
    n: Expr

    def compile(self) -> Any:
        return {
            "$maxN": {
                "input": compile(self.value),
                "n": compile(self.n),
            },
        }


@dataclass
class Median(Accumulator):
    """Returns an approximation of the median value."""

    input: Expr

    def compile(self) -> Any:
        return {
            "$median": {
                "input": compile(self.input),
                "method": "approximate",
            },
        }


@dataclass
class MergeObjects(Accumulator):
    """Combines multiple documents into a single document."""

    objects: Expr

    def compile(self) -> Any:
        return {
            "$mergeObjects": compile(self.objects),
        }


@dataclass
class Min(Accumulator):
    """Returns the minimum value."""

    value: Expr

    def compile(self) -> Any:
        return {
            "$min": compile(self.value),
        }


@dataclass
class MinN(Accumulator):
    """Returns an aggregation of the n minimum valued elements within a group."""

    value: Expr
    n: Expr

    def compile(self) -> Any:
        return {
            "$minN": {
                "input": compile(self.value),
                "n": compile(self.n),
            },
        }


@dataclass
class Percentile(Accumulator):
    """Returns an approximation of a percentile value."""

    input: Expr
    p: Expr

    def compile(self) -> Any:
        return {
            "$percentile": {
                "input": compile(self.input),
                "p": compile(self.p),
                "method": "approximate",
            },
        }


@dataclass
class Push(Accumulator):
    """Returns an array of expression values for documents in each group."""

    value: Expr

    def compile(self) -> Any:
        return {
            "$push": compile(self.value),
        }


@dataclass
class StdDevPop(Accumulator):
    """Returns the population standard deviation of the input values."""

    value: Expr
    p: Expr

    def compile(self) -> Any:
        return {
            "$stdDevPop": compile(self.value),
        }


@dataclass
class StdDevSamp(Accumulator):
    """Returns the sample standard deviation of the input values."""

    value: Expr
    p: Expr

    def compile(self) -> Any:
        return {
            "$stdDevSamp": compile(self.value),
        }


@dataclass
class Sum(Accumulator):
    """Returns the sum of numeric values."""

    value: Expr

    def compile(self) -> Any:
        return {"$sum": compile(self.value)}


@dataclass
class Top(Accumulator):
    """Returns the top element within a group according to the specified sort order."""

    sort_by: Any
    output: Expr

    def compile(self) -> Any:
        return {
            "$top": {
                "sortBy": compile(self.sort_by),
                "output": compile(self.output),
            },
        }


@dataclass
class TopN(Accumulator):
    """Returns an aggregation of the top n elements within a group, according to the specified sort order."""

    n: Expr
    sort_by: Any
    output: Expr

    def compile(self) -> Any:
        return {
            "$topN": {
                "n": compile(self.n),
                "sortBy": compile(self.sort_by),
                "output": compile(self.output),
            },
        }


def compile(obj: Any) -> Any:
    if isinstance(obj, Accumulator):
        return obj.compile()
    if isinstance(obj, Path):
        return "$" + obj.value
    return obj
