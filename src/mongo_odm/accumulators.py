from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class Accumulator(ABC):
    @abstractmethod
    def compile(self) -> Any: ...


@dataclass
class Sum(Accumulator):
    value: Any

    def compile(self) -> Any:
        return {"$sum": compile(self.value)}


def compile(obj: Any) -> Any:
    if isinstance(obj, Accumulator):
        return obj.compile()
    return obj
