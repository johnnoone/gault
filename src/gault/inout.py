from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, TypeAlias

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime, timezone
    from decimal import Decimal
    from re import Pattern

    from annotated_types import Predicate
    from bson import Binary as BSONBinary
    from bson import Decimal128, ObjectId, Timestamp
    from bson import Regex as BSONRegex

    from .types import AsRef, ExpressionOperator

    Input: TypeAlias = Any
    Output: TypeAlias = Any

    String: TypeAlias = str
    Binary: TypeAlias = bytes | BSONBinary
    Number: TypeAlias = int | float | Decimal | Decimal128
    Date: TypeAlias = datetime
    Boolean: TypeAlias = bool
    Timezone: TypeAlias = str | timezone
    Array: TypeAlias = list
    Object: TypeAlias = Mapping
    Regex: TypeAlias = str | BSONRegex | Pattern
    MongoPurExpression: TypeAlias = Mapping[str, Any]
    MongoExpression: TypeAlias = (
        MongoPurExpression
        | Mapping[str, Any]
        | list
        | str
        | bytes
        | int
        | float
        | bool
        | ObjectId
        | datetime
        | None
    )
    """Opaque object that resolves to something"""

    Value: TypeAlias = Any

    DollarString = Annotated[str, Predicate(lambda x: str.startswith(x, "$"))]

    PathLike: TypeAlias = DollarString | AsRef
    FieldLike: TypeAlias = (
        Annotated[str, Predicate(lambda x: not str.startswith(x, "$"))] | AsRef
    )

    NumberExpression: TypeAlias = (
        Number | PathLike | MongoPurExpression | ExpressionOperator
    )

    DateExpression: TypeAlias = (
        Date | PathLike | MongoPurExpression | ExpressionOperator
    )
    AnyExpression: TypeAlias = (
        Value | PathLike | MongoPurExpression | ExpressionOperator
    )
    StringExpression: TypeAlias = (
        String | PathLike | MongoPurExpression | ExpressionOperator
    )
    BinaryExpression: TypeAlias = (
        Binary | PathLike | MongoPurExpression | ExpressionOperator
    )
    ArrayExpression: TypeAlias = (
        Array | PathLike | MongoPurExpression | ExpressionOperator
    )
    ObjectExpression: TypeAlias = (
        Object | PathLike | MongoPurExpression | ExpressionOperator
    )
    BooleanExpression: TypeAlias = (
        Boolean | PathLike | MongoPurExpression | ExpressionOperator
    )
    TimestampExpression: TypeAlias = (
        Timestamp | PathLike | MongoPurExpression | ExpressionOperator
    )
    TimezoneExpression: TypeAlias = (
        Timezone | PathLike | MongoPurExpression | ExpressionOperator
    )
    RegexExpression: TypeAlias = (
        Regex | PathLike | MongoPurExpression | ExpressionOperator
    )

    AccumulatorExpression: TypeAlias = Mapping[DollarString, Any]
