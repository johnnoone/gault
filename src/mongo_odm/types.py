from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any

from annotated_types import Predicate

if TYPE_CHECKING:
    from .models import Model, Projection


@dataclass
class Path:
    value: str


type Document = dict[str, Any]
RawPath = Annotated[str, Predicate(lambda x: x.startswith("$"))]
RawField = Annotated[str, Predicate(lambda x: not x.startswith("$"))]


class AttributeBase:
    __slots__ = ("db_alias", "name", "owner")

    def __init__(
        self,
        owner: type[Model | Projection],
        name: str,
        db_alias: str | None = None,
    ) -> None:
        self.owner = owner
        self.name = name
        self.db_alias = db_alias or name
