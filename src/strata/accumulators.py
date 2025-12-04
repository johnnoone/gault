from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

type Expr = Any


class Accumulator(ABC):
    @abstractmethod
    def compile(self) -> Any: ...


@dataclass
class AddToSet(Accumulator):
    expr: Expr

    def compile(self) -> Any:
        return {"$addToSet": compile(self.expr)}


@dataclass
class Avg(Accumulator):
    expr: Expr

    def compile(self) -> Any:
        return {"$avg": compile(self.expr)}


@dataclass
class Bottom(Accumulator):
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
    def compile(self) -> Any:
        return {"$count": {}}


@dataclass
class First(Accumulator):
    value: Expr

    def compile(self) -> Any:
        return {
            "$first": compile(self.value),
        }


@dataclass
class FirstN(Accumulator):
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
    value: Expr

    def compile(self) -> Any:
        return {
            "$last": compile(self.value),
        }


@dataclass
class LastN(Accumulator):
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
    value: Expr

    def compile(self) -> Any:
        return {
            "$max": compile(self.value),
        }


@dataclass
class MaxN(Accumulator):
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
    objects: Expr

    def compile(self) -> Any:
        return {
            "$mergeObjects": compile(self.objects),
        }


@dataclass
class Min(Accumulator):
    value: Expr

    def compile(self) -> Any:
        return {
            "$min": compile(self.value),
        }


@dataclass
class MinN(Accumulator):
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
    input: Expr
    p: Expr

    def compile(self) -> Any:
        return {
            "$percentile": {
                "input": compile(self.value),
                "p": compile(self.p),
                "method": "approximate",
            },
        }


@dataclass
class Push(Accumulator):
    value: Expr

    def compile(self) -> Any:
        return {
            "$push": compile(self.value),
        }


@dataclass
class StdDevPop(Accumulator):
    value: Expr
    p: Expr

    def compile(self) -> Any:
        return {
            "$stdDevPop": compile(self.value),
        }


@dataclass
class StdDevSamp(Accumulator):
    value: Expr
    p: Expr

    def compile(self) -> Any:
        return {
            "$stdDevSamp": compile(self.value),
        }


@dataclass
class Sum(Accumulator):
    value: Expr

    def compile(self) -> Any:
        return {"$sum": compile(self.value)}


@dataclass
class Top(Accumulator):
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
    return obj
