"""Described here https://www.mongodb.com/docs/manual/reference/mql/expressions/."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, overload
from typing import Literal as TypingLiteral

from .compilers import compile_expression, compile_field, compile_query
from .types import (
    FieldUtilInterface,
)
from .sorting import normalize_sort
from .types import (
    Aliased,
    Array,
    AsAlias,
    AsRef,
    Binary,
    Boolean,
    Context,
    Date,
    DateUnit,
    DayWeek,
    Direction,
    FieldSortInterface,
    MongoExpression,
    MongoQuery,
    MongoVar,
    Null,
    Number,
    Object,
    QueryPredicate,
    String,
    Timezone,
)
from .types import (
    ExpressionOperator as _ExpressionOperator,
)
from .utils import nullfree_dict, nullfree_list, unwrap_array

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from bson import ObjectId, Timestamp

    from .predicates import Field


class ExpressionOperator(_ExpressionOperator, AsAlias):
    pass


@dataclass()
class Abs(ExpressionOperator):
    """Returns the absolute value of a number."""

    input: MongoExpression[Number]

    def compile_expression(self, context: Context) -> MongoExpression[Number]:
        return {
            "$abs": compile_expression(self.input, context=context),
        }


@dataclass()
class Acos(ExpressionOperator):
    """Returns the inverse cosine (arc cosine) of a value."""

    input: MongoExpression[Number]
    """any valid expression that resolves to a number between `-1` and `1`.
    """

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$acos": compile_expression(self.input, context=context),
        }


@dataclass()
class Acosh(ExpressionOperator):
    """Returns the inverse hyperbolic cosine (hyperbolic arc cosine) of a value."""

    input: MongoExpression[Number]
    """Any valid expression that resolves to a number between `1` and `+Infinity`."""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$acosh": compile_expression(self.input, context=context),
        }


class Add(ExpressionOperator):
    """Adds numbers together or adds numbers and a date.

    If one of the arguments is a date, $add treats the other arguments as milliseconds to add to the date.
    """

    inputs: list[MongoExpression[Number | Date]]
    """any valid expressions as long as they resolve to either all numbers or to numbers and a date."""

    @overload
    def __init__(self, input: list[MongoExpression], /) -> None: ...

    @overload
    def __init__(self, *inputs: MongoExpression) -> None: ...

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 2:
            msg = "Multiple values is required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Date | Number]:
        return {
            "$add": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class AllElementsTrue(ExpressionOperator):
    """Evaluates an array as a set and returns `true` if no element in the array is `false`."""

    input: MongoExpression[Array]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$allElementsTrue": [
                compile_expression(self.input, context=context),
            ],
        }


class And(QueryPredicate, ExpressionOperator):
    """Evaluates an array as a set and returns `true` if no element in the array is `false`."""

    inputs: list[MongoQuery | MongoExpression[Boolean]]
    """any valid expressions as long as they resolve to either all numbers or to numbers and a date."""

    @overload
    def __init__(self, input: list[MongoExpression], /) -> None: ...

    @overload
    def __init__(self, *inputs: MongoExpression) -> None: ...

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 1:
            msg = "Multiple inputs is required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            "$and": [compile_query(input, context=context) for input in self.inputs],
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$and": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class AnyElementsTrue(ExpressionOperator):
    """Evaluates an array as a set and returns `true` if any of the elements are `true` and `false` otherwise. An empty array returns false."""

    input: MongoExpression[Array]

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$anyElementsTrue": [
                compile_expression(self.input, context=context),
            ],
        }


@dataclass
class ArrayElemAt(ExpressionOperator):
    """Returns the element at the specified array index."""

    input: MongoExpression[Array]

    index: MongoExpression[Number] = field(kw_only=True)

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$arrayElemAt": [
                compile_expression(self.input, context=context),
                compile_expression(self.index, context=context),
            ],
        }


@dataclass
class ArrayToObject(ExpressionOperator):
    """Converts an array into a single document."""

    input: MongoExpression[Array]
    """
    Any valid expression that resolves to:

    - An array of two-element arrays where the first element is the field name,
      and the second element is the field value
    - An array of documents that contains two fields, `k` and `v`
    """

    def compile_expression(self, *, context: Context) -> MongoExpression[Object]:
        return {
            "$arrayToObject": compile_expression(self.input, context=context),
        }


@dataclass
class Asin(ExpressionOperator):
    """Returns the inverse sine (arc sine) of a value."""

    input: MongoExpression[Number]
    """any valid expression that resolves to a number between `-1` and `1`.
    """

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$asin": compile_expression(self.input, context=context)}


@dataclass
class Asinh(ExpressionOperator):
    """Returns the inverse hyperbolic sine (hyperbolic arc sine) of a value."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$asinh": compile_expression(self.input, context=context)}


@dataclass
class Atan(ExpressionOperator):
    """Returns the inverse tangent (arc tangent) of a value."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$atan": compile_expression(self.input, context=context)}


@dataclass
class Atan2(ExpressionOperator):
    """Returns the inverse tangent (arc tangent) of y / x, where y and x are the first and second values passed to the expression respectively."""

    x: MongoExpression[Number]

    y: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$atan2": [
                compile_expression(self.x, context=context),
                compile_expression(self.y, context=context),
            ],
        }


@dataclass
class Atanh(ExpressionOperator):
    """Returns the inverse hyperbolic tangent (hyperbolic arc tangent) of a value."""

    input: MongoExpression[Number]
    """any valid expression that resolves to a number between -1 and 1
    """

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$atanh": compile_expression(self.input, context=context)}


@dataclass
class BinarySize(ExpressionOperator):
    """Returns the size of a given string or binary data value's content in bytes."""

    input: MongoExpression[String | Binary]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$binarySize": compile_expression(self.input, context=context)}


@dataclass
class BitAnd(ExpressionOperator):
    """Returns the result of a bitwise and operation on an array of int or long values."""

    inputs: list[MongoExpression[Number]]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 2:
            msg = "Multiple values required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$bitAnd": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class BitNot(ExpressionOperator):
    """Returns the result of a bitwise `not` operation on a single int or long value."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$bitNot": compile_expression(self.input, context=context),
        }


class BitOr(ExpressionOperator):
    """Returns the result of a bitwise `or` operation on an array of int and long values."""

    inputs: list[MongoExpression[Number]]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 2:
            msg = "Multiple values required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$bitOr": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


class BitXor(ExpressionOperator):
    """Returns the result of a bitwise `xor` (exclusive or) operation on an array of int and long values."""

    inputs: list[MongoExpression[Number]]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if not inputs:
            msg = "Values is required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$bitXor": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class BsonSize(ExpressionOperator):
    """Returns the size in bytes of a given document (i.e. bsontype Object) when encoded as BSON."""

    input: MongoExpression[Object | Null]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$bsonSize": compile_expression(self.input, context=context),
        }


@dataclass
class Ceil(ExpressionOperator):
    """Returns the smallest integer greater than or equal to the specified number."""

    input: MongoExpression[Number]

    def compile_expression(self, context: Context) -> MongoExpression:
        return {"$ceil": compile_expression(self.input, context=context)}


@dataclass
class Cmp(ExpressionOperator):
    """Compares two values.

    Returns this:
    - -1 if the first value is less than the second.
    - 1 if the first value is greater than the second.
    - 0 if the two values are equivalent.
    """

    lhs: MongoExpression
    rhs: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$cmp": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


class Concat(ExpressionOperator):
    """Concatenates strings and returns the concatenated string."""

    inputs: list[MongoExpression[String]]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if not inputs:
            msg = "Values is required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[String | Null]:
        return {
            "$concat": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


class ConcatArrays(ExpressionOperator):
    """Returns a single array that concatenates two or more arrays."""

    inputs: list[MongoExpression[Array]]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if not inputs:
            msg = "Values is required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$concatArrays": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class Cond(ExpressionOperator):
    """Evaluates a boolean expression to return one of the two specified return expressions."""

    when: MongoExpression[Boolean]

    then: MongoExpression

    otherwise: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$cond": {
                "if": compile_expression(self.when, context=context),
                "then": compile_expression(self.then, context=context),
                "else": compile_expression(self.otherwise, context=context),
            },
        }


@dataclass
class Cos(ExpressionOperator):
    """Returns the cosine of a value that is measured in radians."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {"$cos": compile_expression(self.input, context=context)}


@dataclass
class Cosh(ExpressionOperator):
    """Returns the hyperbolic cosine of a value that is measured in radians."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$cosh": compile_expression(self.input, context=context)}


@dataclass
class DateAdd(ExpressionOperator):
    """Increments a Date() object by a specified number of time units."""

    start_date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    unit: MongoExpression[DateUnit]

    amount: MongoExpression[Number]

    timezone: MongoExpression | None = None
    """valid expression that resolves to a string formatted as either an
    Olson Timezone Identifier or a UTC Offset."""

    def compile_expression(self, *, context: Context) -> MongoExpression[Date]:
        return {
            "$dateAdd": nullfree_dict(
                {
                    "startDate": compile_expression(self.start_date, context=context),
                    "unit": compile_expression(self.unit, context=context),
                    "amount": compile_expression(self.amount, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class DateDiff(ExpressionOperator):
    """Returns the difference between two dates."""

    start_date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    end_date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    unit: MongoExpression[DateUnit]

    timezone: MongoExpression[Timezone] | None = None

    start_of_week: MongoExpression[DayWeek] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$dateDiff": nullfree_dict(
                {
                    "startDate": compile_expression(self.start_date, context=context),
                    "endDate": compile_expression(self.end_date, context=context),
                    "unit": compile_expression(self.unit, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                    "startOfWeek": compile_expression(
                        self.start_of_week,
                        context=context,
                    ),
                },
            ),
        }


@dataclass
class DateFromParts(ExpressionOperator):
    """Constructs and returns a Date object given the date's constituent properties."""

    year: MongoExpression[Number] | None = None
    iso_week_year: MongoExpression[Number] | None = None
    month: MongoExpression[Number] | None = None
    iso_week: MongoExpression[Number] | None = None
    day: MongoExpression[Number] | None = None
    iso_day_of_week: MongoExpression[Number] | None = None
    hour: MongoExpression[Number] | None = None
    minute: MongoExpression[Number] | None = None
    second: MongoExpression[Number] | None = None
    millisecond: MongoExpression[Number] | None = None
    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(
        self,
        *,
        context: Context,
    ) -> MongoExpression[Date]:
        return {
            "$dateFromParts": nullfree_dict(
                {
                    "year": compile_expression(self.year, context=context),
                    "isoWeekYear": compile_expression(
                        self.iso_week_year,
                        context=context,
                    ),
                    "month": compile_expression(self.month, context=context),
                    "isoWeek": compile_expression(self.iso_week, context=context),
                    "day": compile_expression(self.day, context=context),
                    "isoDayOfWeek": compile_expression(
                        self.iso_day_of_week,
                        context=context,
                    ),
                    "hour": compile_expression(self.hour, context=context),
                    "minute": compile_expression(self.minute, context=context),
                    "second": compile_expression(self.second, context=context),
                    "millisecond": compile_expression(
                        self.millisecond,
                        context=context,
                    ),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class DateFromString(ExpressionOperator):
    """Converts a date/time string to a date object."""

    date_string: MongoExpression[String]
    """The date/time string to convert to a date object."""

    format: str | None = None
    """The date format specification of the dateString..
    """

    timezone: MongoExpression[Timezone] | None = None
    """valid expression that resolves to a string formatted as either an
    Olson Timezone Identifier or a UTC Offset."""

    on_error: MongoExpression | None = None
    """any valid expression.
    """

    on_null: MongoExpression | None = None
    """any valid expression.
    """

    def compile_expression(self, *, context: Context) -> MongoExpression[Date]:
        return {
            "$dateFromString": nullfree_dict(
                {
                    "dateString": compile_expression(self.date_string, context=context),
                    "format": compile_expression(self.format, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                    "onError": compile_expression(self.on_error, context=context),
                    "onNull": compile_expression(self.on_null, context=context),
                },
            ),
        }


@dataclass
class DateSubtract(ExpressionOperator):
    """Decrements a Date() object by a specified number of time units."""

    start_date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    unit: MongoExpression[DateUnit]

    amount: MongoExpression[Number]

    timezone: MongoExpression[Timezone] | None = None
    """valid expression that resolves to a string formatted as either an
    Olson Timezone Identifier or a UTC Offset."""

    def compile_expression(self, *, context: Context) -> MongoExpression[Date]:
        return {
            "$dateSubtract": nullfree_dict(
                {
                    "startDate": compile_expression(self.start_date, context=context),
                    "unit": compile_expression(self.unit, context=context),
                    "amount": compile_expression(self.amount, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class DateToParts(ExpressionOperator):
    """Returns a document that contains the constituent parts of a given BSON Date value as individual properties."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    timezone: MongoExpression[Timezone] | None = None
    """valid expression that resolves to a string formatted as either an
    Olson Timezone Identifier or a UTC Offset."""

    iso8601: bool | None = None
    """modifies the output document to use ISO week date fields"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Object]:
        return {
            "$dateToParts": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                    "iso8601": compile_expression(self.iso8601, context=context),
                },
            ),
        }


@dataclass
class DateToString(ExpressionOperator):
    """Converts a date object to a string according to a user-specified format."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    format: str | None = None
    """modifies the output document to use ISO week date fields"""

    timezone: MongoExpression[Timezone] | None = None
    """valid expression that resolves to a string formatted as either an
    Olson Timezone Identifier or a UTC Offset."""

    on_null: MongoExpression | None = None
    """modifies the output document to use ISO week date fields"""

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$dateToString": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "format": compile_expression(self.format, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                    "onNull": compile_expression(self.on_null, context=context),
                },
            ),
        }


@dataclass
class DateTrunc(ExpressionOperator):
    """Truncates a date."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    unit: MongoExpression[DateUnit]

    bin_size: MongoExpression[Number] | None = None
    """an expression that must resolve to a positive non-zero number"""

    timezone: MongoExpression[Timezone] | None = None
    """valid expression that resolves to a string formatted as either an
    Olson Timezone Identifier or a UTC Offset."""

    start_of_week: MongoExpression[DayWeek] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Date]:
        return {
            "$dateTrunc": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "unit": compile_expression(self.unit, context=context),
                    "binSize": compile_expression(self.bin_size, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                    "startOfWeek": compile_expression(
                        self.start_of_week,
                        context=context,
                    ),
                },
            ),
        }


@dataclass
class DayOfMonth(ExpressionOperator):
    """Returns the day of the month for a date as a number between 1 and 31."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$dayOfMonth": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class DayOfWeek(ExpressionOperator):
    """Returns the day of the week for a date as a number between 1 (Sunday) and 7 (Saturday)."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$dayOfWeek": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class DayOfYear(ExpressionOperator):
    """Returns the day of the year for a date as a number between 1 and 366."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$dayOfYear": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class DegreesToRadians(ExpressionOperator):
    """Converts an input value measured in degrees to radians."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$degreesToRadians": compile_expression(self.input, context=context)}


@dataclass
class Divide(ExpressionOperator):
    """Divides one number by another and returns the result."""

    dividende: MongoExpression[Number]
    """any valid expression as long as they resolve to numbers"""

    divisor: MongoExpression[Number]
    """any valid expression as long as they resolve to numbers"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$divide": [
                compile_expression(self.dividende, context=context),
                compile_expression(self.divisor, context=context),
            ],
        }


@dataclass
class Eq(QueryPredicate, ExpressionOperator):
    """Compares two values.

    It returns:
    - true when the values are equivalent.
    - false when the values are not equivalent.
    """

    lhs: MongoExpression
    rhs: MongoExpression

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            compile_field(self.lhs, context=context): {
                "$eq": compile_expression(self.rhs, context=context),
            },
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$eq": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


@dataclass
class Exp(ExpressionOperator):
    """Raises Euler's number to the specified exponent and returns the result."""

    exponent: MongoExpression[Number]
    """any valid expression as long as it resolves to a number"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$exp": compile_expression(self.exponent, context=context),
        }


@dataclass
class Filter(ExpressionOperator):
    """Selects a subset of an array to return based on the specified condition."""

    input: MongoExpression[Array]
    var: str | None = field(default=None, kw_only=True)
    cond: MongoExpression[Boolean] | Callable[[Var, Context], MongoExpression[Boolean]]
    limit: MongoExpression[Number] | None = field(default=None, kw_only=True)

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        var = self.var
        if isinstance(var, str):
            var = Var(var)

        if self.cond and callable(self.cond):
            var = var or Var("this")
            cond = self.cond(var, context)
        else:
            cond = self.cond

        return {
            "$filter": nullfree_dict(
                {
                    "input": compile_expression(self.input, context=context),
                    "as": compile_field(var, context=context) if self.var else None,
                    "cond": compile_expression(cond, context=context),
                    "limit": compile_expression(self.limit, context=context),
                },
            ),
        }


@dataclass
class Floor(ExpressionOperator):
    """Returns the largest integer less than or equal to the specified number."""

    input: MongoExpression[Number]

    def compile_expression(self, context: Context) -> MongoExpression[Number]:
        return {"$floor": compile_expression(self.input, context=context)}


@dataclass
class GetField(ExpressionOperator):
    """Returns the value of a specified field from a document."""

    field: MongoExpression[None]
    """any valid expression that resolves to a string."""

    input: MongoExpression[Object] | None = None
    """valid expression that contains the field for which you want to return a value.
    input must resolve to an object, missing, null, or undefined."""

    def compile_expression(self, context: Context) -> MongoExpression:
        return {
            "$getField": nullfree_dict(
                {
                    "field": compile_expression(self.field, context=context),
                    "input": compile_expression(self.input, context=context),
                },
            ),
        }


@dataclass
class Gt(QueryPredicate, ExpressionOperator):
    """Compares two values.

    It returns:
    - `true` when the first value is greater than the second value
    - `false` when the first value is less than or equal to the second value
    """

    lhs: MongoExpression
    rhs: MongoExpression

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            compile_field(self.lhs, context=context): {
                "$gt": compile_expression(self.rhs, context=context),
            },
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$gt": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


@dataclass
class Gte(QueryPredicate, ExpressionOperator):
    """Compares two values.

    It returns:
    - `true` when the first value is greater than or equal to the second value
    - `false` when the first value is less than or equal to the second value
    """

    lhs: MongoExpression
    rhs: MongoExpression

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            compile_field(self.lhs, context=context): {
                "$gte": compile_expression(self.rhs, context=context),
            },
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$gte": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


@dataclass
class Hour(ExpressionOperator):
    """Returns the hour portion of a date as a number between 0 and 23."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$hour": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


class IfNull(ExpressionOperator):
    """The $ifNull expression evaluates input expressions for null values.

    It returns:
    - The first non-null input expression value found.
    - A replacement expression value if all input expressions evaluate to null.
    """

    inputs: list[MongoExpression]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 1:
            msg = "Multiple inputs is required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$ifNull": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class In(QueryPredicate, ExpressionOperator):
    """Returns a boolean indicating whether a specified value is in an array."""

    lhs: MongoExpression
    """Any valid expression expression."""

    rhs: MongoExpression[Array]

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            compile_field(self.lhs, context=context): {
                "$in": compile_expression(self.rhs, context=context),
            },
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$in": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


@dataclass
class IndexOfArray(ExpressionOperator):
    """Searches an array for an occurrence of a specified value and returns the array index of the first occurrence."""

    input: MongoExpression[Array]

    search: MongoExpression

    start: MongoExpression[Number] | None = None
    """any valid expression that resolves to a non-negative integral number."""

    end: MongoExpression[Number] | None = None
    """any valid expression that resolves to a non-negative integral number."""

    def __post_init__(self) -> None:
        if self.end:
            self.start = self.start or 0

    def compile_expression(self, *, context: Context) -> MongoExpression[Number | Null]:
        return {
            "$indexOfArray": nullfree_list(
                [
                    compile_expression(self.input, context=context),
                    compile_expression(self.search, context=context),
                    compile_expression(self.start, context=context),
                    compile_expression(self.end, context=context),
                ],
            ),
        }


@dataclass
class IndexOfBytes(ExpressionOperator):
    """Searches a string for an occurrence of a substring and returns the UTF-8 byte index (zero-based) of the first occurrence."""

    input: MongoExpression[String]
    """any valid expression as long as it resolves to a string"""

    search: MongoExpression
    """any valid expression as long as it resolves to a string"""

    start: MongoExpression[Number] | None = None
    """any valid expression that resolves to a non-negative integral number."""

    end: MongoExpression[Number] | None = None
    """any valid expression that resolves to a non-negative integral number."""

    def __post_init__(self) -> None:
        if self.end:
            self.start = self.start or 0

    def compile_expression(self, *, context: Context) -> MongoExpression[Number | Null]:
        return {
            "$indexOfBytes": nullfree_list(
                [
                    compile_expression(self.input, context=context),
                    compile_expression(self.search, context=context),
                    compile_expression(self.start, context=context),
                    compile_expression(self.end, context=context),
                ],
            ),
        }


@dataclass
class IndexOfCP(ExpressionOperator):
    """Searches a string for an occurrence of a substring and returns the UTF-8 code point index (zero-based) of the first occurrence."""

    input: MongoExpression[String]
    """any valid expression as long as it resolves to a string"""

    search: MongoExpression
    """any valid expression as long as it resolves to a string"""

    start: MongoExpression[Number] | None = None
    """any valid expression that resolves to a non-negative integral number."""

    end: MongoExpression[Number] | None = None
    """any valid expression that resolves to a non-negative integral number."""

    def __post_init__(self) -> None:
        if self.end:
            self.start = self.start or 0

    def compile_expression(self, *, context: Context) -> MongoExpression[Number | Null]:
        return {
            "$indexOfCP": nullfree_list(
                [
                    compile_expression(self.input, context=context),
                    compile_expression(self.search, context=context),
                    compile_expression(self.start, context=context),
                    compile_expression(self.end, context=context),
                ],
            ),
        }


@dataclass
class IsArray(ExpressionOperator):
    """Determines if the operand is an array."""

    input: MongoExpression
    """any valid expression."""

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$isArray": [compile_expression(self.input, context=context)],
        }


@dataclass
class IsNumber(ExpressionOperator):
    """Determines if the operand is a number."""

    input: MongoExpression
    """any valid expression."""

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$isNumber": compile_expression(self.input, context=context),
        }


@dataclass
class IsoDayOfWeek(ExpressionOperator):
    """Returns the weekday number in ISO 8601 format, ranging from 1 (for Monday) to 7 (for Sunday)."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$isoDayOfWeek": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class IsoWeek(ExpressionOperator):
    """Returns the week number in ISO 8601 format, ranging from 1 to 53."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$isoWeek": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class IsoWeekYear(ExpressionOperator):
    """Returns the year number in ISO 8601 format."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$isoWeekYear": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class Let(ExpressionOperator):
    """Binds variables for use in the specified expression, and returns the result of the expression."""

    variables: dict[MongoVar, MongoExpression]
    """Assignment block for the variables accessible in the in expression."""

    into: MongoExpression = field(kw_only=True)
    """The expression to evaluate."""

    @overload
    def __init__(
        self, variables: dict[MongoVar, MongoExpression], /, into: MongoExpression
    ) -> None: ...

    @overload
    def __init__(self, *variables: Aliased, into: MongoExpression) -> None: ...

    def __init__(self, *variables: Any, into: MongoExpression) -> None:
        spec = {}
        if len(variables) == 1 and isinstance(variables[0], dict):
            spec |= variables[0]
        else:
            for aliased in variables:
                assert isinstance(aliased, Aliased)  # noqa: S101
                spec[aliased.ref] = aliased.value
        self.variables = spec
        self.into = into

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$let": {
                "vars": {
                    compile_field(key, context=context): compile_expression(
                        val,
                        context=context,
                    )
                    for key, val in self.variables.items()
                },
                "in": compile_expression(self.into, context=context),
            },
        }


@dataclass
class Literal(ExpressionOperator):
    """Returns a value without parsing."""

    input: Any

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$literal": self.input,
        }


@dataclass
class Ln(ExpressionOperator):
    """Calculates the natural logarithm ln (i.e log e) of a number and returns the result as a double."""

    input: MongoExpression[Number]
    """Any valid expression as long as it resolves to a non-negative number"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {"$ln": compile_expression(self.input, context=context)}


@dataclass
class Log(ExpressionOperator):
    """Calculates the log of a number in the specified base and returns the result as a double."""

    input: MongoExpression[Number]
    """any valid expression as long as it resolves to a non-negative number"""

    base: MongoExpression
    """any valid expression as long as it resolves to a positive number greater than 1"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$log": [
                compile_expression(self.input, context=context),
                compile_expression(self.base, context=context),
            ],
        }


@dataclass
class Log10(ExpressionOperator):
    """Calculates the log base 10 of a number and returns the result as a double."""

    input: MongoExpression[Number]
    """any valid expression as long as it resolves to a non-negative number"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$log10": compile_expression(self.input, context=context),
        }


@dataclass
class Lt(QueryPredicate, ExpressionOperator):
    """Compares two values.

    It returns:
    - `true` when the first value less than than the second value
    - `false` when the first value is greater than or equivalent to the second value
    """

    lhs: MongoExpression
    rhs: MongoExpression

    def compile_query(self, *, context: Context) -> MongoQuery[Boolean]:
        return {
            compile_field(self.lhs, context=context): {
                "$lt": compile_expression(self.rhs, context=context),
            },
        }

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$lt": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


@dataclass
class Lte(QueryPredicate, ExpressionOperator):
    """Compares two values.

    It returns:
    - `true` when the first value is less than or equivalent or equal to the second value
    - `false` when the first value is greater than the second value
    """

    lhs: MongoExpression
    rhs: MongoExpression

    def compile_query(self, *, context: Context) -> MongoQuery[Boolean]:
        return {
            compile_field(self.lhs, context=context): {
                "$lte": compile_expression(self.rhs, context=context),
            },
        }

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$lte": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


@dataclass
class Ltrim(ExpressionOperator):
    """Removes whitespace characters, including null, or the specified characters from the beginning of a string."""

    input: MongoExpression[String]
    """any valid expression that resolves to a string"""

    chars: MongoExpression[String]
    """any valid expression that resolves to a string"""

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$ltrim": {
                "input": compile_expression(self.input, context=context),
                "chars": compile_expression(self.chars, context=context),
            },
        }


@dataclass
class Map(ExpressionOperator):
    """Applies an expression to each item in an array and returns an array with the applied results."""

    input: MongoExpression[Array]
    """any valid expression that resolves to an array"""

    var: MongoExpression[String] | None = field(default=None, kw_only=True)
    """A name for the variable that represents each individual element of the input array. If no name is specified, the variable name defaults to this"""

    into: MongoExpression
    """An expression that is applied to each element of the input array"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        var = self.var
        if isinstance(var, str):
            var = Var(var)

        if callable(self.into):
            var = var or Var("this")
            expression = self.into(var, context)
        else:
            expression = self.into

        return {
            "$map": nullfree_dict(
                {
                    "input": compile_expression(self.input, context=context),
                    "as": compile_field(var, context=context) if self.var else None,
                    "in": compile_expression(expression, context=context),
                },
            )
        }


@dataclass
class MaxN(ExpressionOperator):
    """Returns the n largest values in an array."""

    input: MongoExpression[Array]
    """An expression that resolves to the array"""

    n: MongoExpression[Number]
    """An expression that resolves to a positive integer"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$maxN": {
                "input": compile_expression(self.input, context=context),
                "n": compile_expression(self.n, context=context),
            },
        }


@dataclass
class Meta(ExpressionOperator):
    """Returns the metadata associated with a document, e.g. "textScore" when performing text search."""

    keyword: TypingLiteral["textScore", "indexKey"]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$meta": self.keyword,
        }


@dataclass
class MinN(ExpressionOperator):
    """Returns the n smallest values in an array."""

    input: MongoExpression[Array]
    """An expression that resolves to the array"""

    n: MongoExpression[Number]
    """An expression that resolves to a positive integer"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$minN": {
                "input": compile_expression(self.input, context=context),
                "n": compile_expression(self.n, context=context),
            },
        }


@dataclass
class Millisecond(ExpressionOperator):
    """Returns the millisecond portion of a date as an integer between 0 and 999."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$millisecond": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class Minute(ExpressionOperator):
    """Returns the minute portion of a date as a number between 0 and 59."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$minute": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class Mod(ExpressionOperator):
    """Divides one number by another and returns the remainder."""

    value1: MongoExpression[Number]
    value2: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$mod": [
                compile_expression(self.value1, context=context),
                compile_expression(self.value2, context=context),
            ],
        }


@dataclass
class Month(ExpressionOperator):
    """Returns the month of a date as a number between 1 and 12."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$month": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class Multiply(ExpressionOperator):
    """Multiplies numbers together and returns the result."""

    inputs: list[MongoExpression[Number]]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$multiply": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class Ne(QueryPredicate, ExpressionOperator):
    """Compares two values.

    It returns:
    - true when the values are not equivalent.
    - false when the values are equivalent.
    """

    lhs: MongoExpression
    rhs: MongoExpression

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            compile_field(self.lhs, context=context): {
                "$ne": compile_expression(self.rhs, context=context),
            },
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$ne": [
                compile_expression(self.lhs, context=context),
                compile_expression(self.rhs, context=context),
            ],
        }


@dataclass
class Not(QueryPredicate, ExpressionOperator):
    """Evaluates a boolean and returns the opposite boolean value."""

    input: MongoExpression

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            "$not": compile_query(self.input, context=context),
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$not": [
                compile_expression(self.input, context=context),
            ],
        }


@dataclass
class ObjectToArray(ExpressionOperator):
    """Converts a document to an array."""

    input: MongoExpression[Object]

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$objectToArray": compile_expression(self.input, context=context),
        }


class Or(QueryPredicate, ExpressionOperator):
    """Evaluates one or more expressions and returns true if any of the expressions are true."""

    inputs: list[MongoExpression]

    def __init__(self, *inputs: MongoExpression) -> None:
        inputs = unwrap_array(inputs)
        if not inputs:
            msg = "Values is required."
            raise ValueError(msg)
        self.inputs = inputs

    def compile_query(self, *, context: Context) -> MongoQuery:
        return {
            "$or": [compile_query(input, context=context) for input in self.inputs],
        }

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$or": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class Pow(ExpressionOperator):
    """Raises a number to the specified exponent and returns the result."""

    input: MongoExpression[Number]
    exponent: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$pow": [
                compile_expression(self.input, context=context),
                compile_expression(self.exponent, context=context),
            ],
        }


@dataclass
class RadiansToDegrees(ExpressionOperator):
    """Converts an input value measured in radians to degrees."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$radiansToDegrees": compile_expression(self.input, context=context),
        }


@dataclass
class Rand(ExpressionOperator):
    """Returns a random float between 0 and 1 each time it is called."""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$rand": {},
        }


@dataclass
class Range(ExpressionOperator):
    """Returns an array whose elements are a generated sequence of numbers."""

    start: MongoExpression[Number]
    end: MongoExpression[Number]
    step: MongoExpression[Number] = 1

    def compile_expression(self, *, context: Context) -> MongoExpression[Array[Number]]:
        return {
            "$range": [
                compile_expression(self.start, context=context),
                compile_expression(self.end, context=context),
                compile_expression(self.step, context=context),
            ],
        }


@dataclass
class Reduce(ExpressionOperator):
    """Applies an expression to each element in an array and combines them into a single value."""

    input: MongoExpression[Array]
    initial_value: MongoExpression
    into: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$reduce": {
                "input": compile_expression(self.input, context=context),
                "initialValue": compile_expression(self.initial_value, context=context),
                "in": compile_expression(self.into, context=context),
            },
        }


@dataclass
class RegexFind(ExpressionOperator):
    """Provides regular expression (regex) pattern matching capability in aggregation expressions."""

    input: MongoExpression[String]
    regex: MongoExpression[String]
    options: MongoExpression[String] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Object | Null]:
        return {
            "$regexFind": nullfree_dict(
                {
                    "input": compile_expression(self.input, context=context),
                    "regex": compile_expression(self.regex, context=context),
                    "options": compile_expression(self.options, context=context),
                },
            ),
        }


@dataclass
class RegexFindAll(ExpressionOperator):
    """Provides regular expression (regex) pattern matching capability in aggregation expressions."""

    input: MongoExpression[String]
    regex: MongoExpression[String]
    options: MongoExpression[String] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Array[Object]]:
        return {
            "$regexFindAll": nullfree_dict(
                {
                    "input": compile_expression(self.input, context=context),
                    "regex": compile_expression(self.regex, context=context),
                    "options": compile_expression(self.options, context=context),
                },
            ),
        }


@dataclass
class RegexMatch(ExpressionOperator):
    """Performs a regular expression (regex) pattern matching."""

    input: MongoExpression[String]
    regex: MongoExpression[String]
    options: MongoExpression
    options: MongoExpression[String] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$regexMatch": nullfree_dict(
                {
                    "input": compile_expression(self.input, context=context),
                    "regex": compile_expression(self.regex, context=context),
                    "options": compile_expression(self.options, context=context),
                },
            ),
        }


@dataclass
class ReplaceOne(ExpressionOperator):
    """Replaces the first instance of a search string in an input string with a replacement string."""

    input: MongoExpression[String]
    find: MongoExpression[String]
    replacement: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$replaceOne": {
                "input": compile_expression(self.input, context=context),
                "find": compile_expression(self.find, context=context),
                "replacement": compile_expression(self.replacement, context=context),
            },
        }


@dataclass
class ReplaceAll(ExpressionOperator):
    """Replaces all instances of a search string in an input string with a replacement string."""

    input: MongoExpression[String]
    find: MongoExpression[String]
    replacement: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$replaceAll": {
                "input": compile_expression(self.input, context=context),
                "find": compile_expression(self.find, context=context),
                "replacement": compile_expression(self.replacement, context=context),
            },
        }


@dataclass
class ReverseArray(ExpressionOperator):
    """Accepts an array expression as an argument and returns an array with the elements in reverse order."""

    input: MongoExpression[Array]

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$reverseArray": compile_expression(self.input, context=context),
        }


@dataclass
class Round(ExpressionOperator):
    """Rounds a number to a whole integer or to a specified decimal place."""

    input: MongoExpression[Number]
    place: MongoExpression[Number] = 0

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$round": [
                compile_expression(self.input, context=context),
                compile_expression(self.place, context=context),
            ],
        }


@dataclass
class Rtrim(ExpressionOperator):
    """Removes whitespace characters, including null, or the specified characters from the end of a string."""

    input: MongoExpression[String]
    """any valid expression that resolves to a string"""

    chars: MongoExpression[String]
    """any valid expression that resolves to a string"""

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$rtrim": {
                "input": compile_expression(self.input, context=context),
                "chars": compile_expression(self.chars, context=context),
            },
        }


@dataclass
class SampleRate(ExpressionOperator, QueryPredicate):
    """Matches a random selection of input documents."""

    number: MongoExpression[Number]
    """any valid expression that resolves to a string"""

    def compile_query(self, *, context: Context) -> MongoExpression:
        return {
            "$sampleRate": compile_expression(self.number, context=context),
        }

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$sampleRate": compile_expression(self.number, context=context),
        }


@dataclass
class Second(ExpressionOperator):
    """Returns the second portion of a date as a number between 0 and 59, but can be 60 to account for leap seconds."""

    date: MongoExpression[Date]
    """any expression that resolves to a Date, a Timestamp, or an ObjectID."""

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$second": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class SetDifference(ExpressionOperator):
    """Takes two sets and returns an array containing the elements that only exist in the first set."""

    inputs1: MongoExpression[Array]

    inputs2: MongoExpression[Array]

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$setDifference": [
                compile_expression(self.inputs1, context=context),
                compile_expression(self.inputs2, context=context),
            ],
        }


@dataclass
class SetEquals(ExpressionOperator):
    """Compares two or more arrays and returns true if they have the same distinct elements and false otherwise."""

    inputs: list[MongoExpression[Array]]

    def __init__(self, *inputs: MongoExpression[Array]) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 2:
            msg = "Requires at least 2 sets"
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$setEquals": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class SetField(ExpressionOperator):
    """Adds, updates, or removes a specified field in a document."""

    input: MongoExpression[Object]
    field: MongoExpression[String]
    value: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$setField": {
                "input": compile_expression(self.input, context=context),
                "field": compile_expression(self.field, context=context),
                "value": compile_expression(self.value, context=context),
            },
        }


@dataclass
class SetIntersection(ExpressionOperator):
    """Takes two or more arrays and returns an array that contains the elements that appear in every input array."""

    inputs: list[MongoExpression[Array]]

    def __init__(self, *inputs: MongoExpression[Array]) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 2:
            msg = "Requires at least 2 sets"
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$setIntersection": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class SetIsSubset(ExpressionOperator):
    """Takes two arrays and returns true when the first array is a subset of the second."""

    input1: MongoExpression[Array]
    input2: MongoExpression[Array]

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$setIsSubset": [
                compile_expression(self.input1, context=context),
                compile_expression(self.input2, context=context),
            ],
        }


@dataclass
class SetUnion(ExpressionOperator):
    """Takes two or more arrays and returns a single array containing the unique elements that appear in any input array."""

    inputs: MongoExpression | list[MongoExpression]

    def __init__(self, *inputs: MongoExpression[Array]) -> None:
        inputs = unwrap_array(inputs)
        if len(inputs) < 2:
            msg = "Requires at least 2 sets"
            raise ValueError(msg)
        self.inputs = inputs

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$setUnion": [
                compile_expression(input, context=context) for input in self.inputs
            ],
        }


@dataclass
class Sigmoid(ExpressionOperator):
    """Performs the sigmoid function, which calculates the percentile of a number in the normal distribution with standard deviation 1."""

    input: MongoExpression[Number]
    on_null: MongoExpression | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$sigmoid": {
                "input": compile_expression(self.input, context=context),
            }
            | nullfree_dict(
                {
                    "onNull": compile_expression(self.on_null, context=context),
                }
            ),
        }


@dataclass
class Size(ExpressionOperator):
    """Counts and returns the total number of items in an array."""

    input: MongoExpression[Array]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$size": compile_expression(self.input, context=context),
        }


@dataclass
class Sin(ExpressionOperator):
    """Returns the sine of a value that is measured in radians."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$sin": compile_expression(self.input, context=context),
        }


@dataclass
class Sinh(ExpressionOperator):
    """Returns the hyperbolic sine of a value that is measured in radians."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$sinh": compile_expression(self.input, context=context),
        }


@dataclass
class Slice(ExpressionOperator):
    """Returns a subset of an array."""

    input: MongoExpression[Array]
    n: MongoExpression[Number] = field(kw_only=True)
    position: MongoExpression[Number] | None = field(default=None, kw_only=True)

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$slice": nullfree_list(
                [
                    compile_expression(self.input, context=context),
                    compile_expression(self.position, context=context),
                    compile_expression(self.n, context=context),
                ],
            ),
        }


@dataclass
class SortArray(ExpressionOperator):
    """Sorts an array based on its elements."""

    input: MongoExpression[Array]
    sort_by: Direction | dict[Field, Direction]

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$sortArray": {
                "input": compile_expression(self.input, context=context),
                "sortBy": normalize_sort(self.sort_by),
            },
        }


@dataclass
class Split(ExpressionOperator):
    """Divides a string into an array of substrings based on a delimiter. $split removes the delimiter and returns the resulting substrings as elements of an array."""

    input: MongoExpression[String]
    delimiter: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[Array[String]]:
        return {
            "$split": [
                compile_expression(self.input, context=context),
                compile_expression(self.delimiter, context=context),
            ],
        }


@dataclass
class Sqrt(ExpressionOperator):
    """Calculates the square root of a positive number and returns the result as a double."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$sqrt": compile_expression(self.input, context=context),
        }


@dataclass
class StrCaseCmp(ExpressionOperator):
    """Performs case-insensitive comparison of two strings."""

    input1: MongoExpression[String]
    input2: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$strcasecmp": [
                compile_expression(self.input1, context=context),
                compile_expression(self.input2, context=context),
            ],
        }


@dataclass
class StrLenBytes(ExpressionOperator):
    """Returns the number of UTF-8 encoded bytes in the specified string."""

    input: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$strLenBytes": compile_expression(self.input, context=context),
        }


@dataclass
class StrLenCP(ExpressionOperator):
    """Returns the number of UTF-8 code points in the specified string."""

    input: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$strLenCP": compile_expression(self.input, context=context),
        }


@dataclass
class SubStrBytes(ExpressionOperator):
    """Returns the substring of a string."""

    input: MongoExpression[String]
    start: MongoExpression[Number]
    length: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$substrBytes": [
                compile_expression(self.input, context=context),
                compile_expression(self.start, context=context),
                compile_expression(self.length, context=context),
            ],
        }


@dataclass
class SubStrCP(ExpressionOperator):
    """Returns the substring of a string."""

    input: MongoExpression[String]
    start: MongoExpression[Number]
    length: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$substrCP": [
                compile_expression(self.input, context=context),
                compile_expression(self.start, context=context),
                compile_expression(self.length, context=context),
            ],
        }


@dataclass
class Subtract(ExpressionOperator):
    """Subtracts two numbers to return the difference, or two dates to return the difference in milliseconds, or a date and a number in milliseconds to return the resulting date."""

    input1: MongoExpression[String | Number | Date]
    input2: MongoExpression[String | Number | Date]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$subtract": [
                compile_expression(self.input1, context=context),
                compile_expression(self.input2, context=context),
            ],
        }


@dataclass
class Switch(ExpressionOperator):
    """Evaluates a series of case expressions."""

    branches: list[tuple[MongoExpression[Boolean], MongoExpression]]
    default: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$switch": {
                "branches": [
                    {
                        "case": compile_expression(case, context=context),
                        "then": compile_expression(then, context=context),
                    }
                    for case, then in self.branches
                ],
                "default": compile_expression(self.default, context=context),
            },
        }


@dataclass
class Tan(ExpressionOperator):
    """Returns the tangent of a value that is measured in radians."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$tan": compile_expression(self.input, context=context),
        }


@dataclass
class Tanh(ExpressionOperator):
    """Returns the hyperbolic tangent of a value that is measured in radians."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$tanh": compile_expression(self.input, context=context),
        }


@dataclass
class ToBool(ExpressionOperator):
    """Converts a value to a boolean."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[Boolean]:
        return {
            "$toBool": compile_expression(self.input, context=context),
        }


@dataclass
class ToDate(ExpressionOperator):
    """Converts a value to a date."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[Date]:
        return {
            "$toDate": compile_expression(self.input, context=context),
        }


@dataclass
class ToDecimal(ExpressionOperator):
    """Converts a value to a decimal."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$toDecimal": compile_expression(self.input, context=context),
        }


@dataclass
class ToDouble(ExpressionOperator):
    """Converts a value to a double."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$toDouble": compile_expression(self.input, context=context),
        }


@dataclass
class ToHashedIndexKey(ExpressionOperator):
    """Computes and returns the hash value of the input expression."""

    input: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$toHashedIndexKey": compile_expression(self.input, context=context),
        }


@dataclass
class ToInt(ExpressionOperator):
    """Converts a value to an integer."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$toInt": compile_expression(self.input, context=context),
        }


@dataclass
class ToLong(ExpressionOperator):
    """Converts a value to a long."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$toLong": compile_expression(self.input, context=context),
        }


@dataclass
class ToObjectId(ExpressionOperator):
    """Converts a value to an ObjectId."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[ObjectId]:
        return {
            "$toObjectId": compile_expression(self.input, context=context),
        }


@dataclass
class ToString(ExpressionOperator):
    """Converts a value to a string."""

    input: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$toString": compile_expression(self.input, context=context),
        }


@dataclass
class ToLower(ExpressionOperator):
    """Converts a string to lowercase, returning the result."""

    input: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$toLower": compile_expression(self.input, context=context),
        }


@dataclass
class ToUpper(ExpressionOperator):
    """Converts a string to uppercase, returning the result."""

    input: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$toUpper": compile_expression(self.input, context=context),
        }


@dataclass
class ToUUID(ExpressionOperator):
    """Converts a string value to a UUID."""

    input: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[UUID]:
        return {
            "$toUUID": compile_expression(self.input, context=context),
        }


@dataclass
class TsIncrement(ExpressionOperator):
    """Returns the incrementing ordinal from a timestamp as a long."""

    input: MongoExpression[Timestamp]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$tsIncrement": compile_expression(self.input, context=context),
        }


@dataclass
class TsSecond(ExpressionOperator):
    """Returns the seconds from a timestamp as a long."""

    input: MongoExpression[Timestamp]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$tsSecond": compile_expression(self.input, context=context),
        }


@dataclass
class Trim(ExpressionOperator):
    """Removes whitespace characters, including null, or the specified characters from the beginning and end of a string."""

    input: MongoExpression[String]
    chars: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$trim": {
                "input": compile_expression(self.input, context=context),
                "chars": compile_expression(self.chars, context=context),
            },
        }


@dataclass
class Trunc(ExpressionOperator):
    """Truncates a number to a whole integer or to a specified decimal place."""

    input: MongoExpression[Number]
    place: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$trunc": [
                compile_expression(self.input, context=context),
                compile_expression(self.place, context=context),
            ],
        }


@dataclass
class Type(ExpressionOperator):
    """Returns a string that specifies the BSON type of the argument."""

    input: MongoExpression[Number]

    def compile_expression(self, *, context: Context) -> MongoExpression[String]:
        return {
            "$type": compile_expression(self.input, context=context),
        }


@dataclass
class UnsetField(ExpressionOperator):
    """Removes a specified field in a document."""

    input: MongoExpression[Object]
    field: MongoExpression[String]

    def compile_expression(self, *, context: Context) -> MongoExpression[Object]:
        return {
            "$unsetField": {
                "input": compile_expression(self.input, context=context),
                "field": compile_expression(self.field, context=context),
            },
        }


@dataclass
class Week(ExpressionOperator):
    """Returns the week of the year for a date as a number between 0 and 53."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$week": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class Year(ExpressionOperator):
    """Returns the year portion of a date."""

    date: MongoExpression[Date]

    timezone: MongoExpression[Timezone] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$year": nullfree_dict(
                {
                    "date": compile_expression(self.date, context=context),
                    "timezone": compile_expression(self.timezone, context=context),
                },
            ),
        }


@dataclass
class Zip(ExpressionOperator):
    """Transposes an array of input arrays."""

    inputs: list[MongoExpression[Array]]
    use_longest_length: bool | None = None
    defaults: MongoExpression[Array] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$zip": {
                "inputs": [
                    compile_expression(input, context=context) for input in self.inputs
                ],
            }
            | nullfree_dict(
                {
                    "useLongestLength": self.use_longest_length,
                    "defaults": compile_expression(self.defaults, context=context),
                }
            ),
        }


class FieldMatcherInterface:
    def abs(self) -> Abs:
        return Abs(self)

    def acos(self) -> Acos:
        return Acos(self)

    def acosh(self) -> Acosh:
        return Acosh(self)

    def add(self, *inputs: MongoExpression) -> Add:
        return Add(self, *inputs)

    def all_elements_true(self, *inputs: MongoExpression) -> AllElementsTrue:
        return AllElementsTrue(self)

    def any_elements_true(self, *inputs: MongoExpression) -> AnyElementsTrue:
        return AnyElementsTrue(self)

    def asin(self) -> Asin:
        return Asin(self)

    def asinh(self) -> Asinh:
        return Asinh(self)

    def atan(self) -> Atan:
        return Atan(self)

    def atan2(self, other: MongoExpression, /) -> Atan2:
        return Atan2(self, other)

    def atanh(self) -> Atanh:
        return Atanh(self)

    def binary_size(self) -> BinarySize:
        return BinarySize(self)

    def bit_and(self, *inputs: MongoExpression) -> BitAnd:
        return BitAnd(self, *inputs)

    def bit_not(self) -> BitNot:
        return BitNot(self)

    def bit_or(self, *inputs: MongoExpression) -> BitOr:
        return BitOr(self, *inputs)

    def bit_xor(self, *inputs: MongoExpression) -> BitXor:
        return BitXor(self, *inputs)

    def bson_size(self) -> BsonSize:
        return BsonSize(self)

    def ceil(self) -> Ceil:
        return Ceil(self)

    def cmp(self, other: MongoExpression, /) -> Cmp:
        return Cmp(self, other)

    def concat(self, *inputs: MongoExpression) -> Concat:
        return Concat(self, *inputs)

    def cos(self) -> Cos:
        return Cos(self)

    def cosh(self) -> Cosh:
        return Cosh(self)

    def date_add(
        self,
        *,
        unit: MongoExpression[DateUnit],
        amount: MongoExpression[Number],
        timezone: MongoExpression | None = None,
    ) -> DateAdd:
        return DateAdd(
            self,
            unit=unit,
            amount=amount,
            timezone=timezone,
        )

    def date_diff(
        self,
        end_date: MongoExpression[Date],
        *,
        unit: MongoExpression[DateUnit],
        timezone: MongoExpression | None = None,
        start_of_week: MongoExpression[DayWeek] | None = None,
    ) -> DateDiff:
        return DateDiff(
            start_date=self,
            end_date=end_date,
            unit=unit,
            start_of_week=start_of_week,
            timezone=timezone,
        )

    def date_from_string(
        self,
        *,
        format: str | None = None,
        timezone: MongoExpression[Timezone] | None = None,
        on_error: MongoExpression | None = None,
        on_null: MongoExpression | None = None,
    ) -> DateFromString:
        return DateFromString(
            self,
            format=format,
            timezone=timezone,
            on_error=on_error,
            on_null=on_null,
        )

    def date_subtract(
        self,
        *,
        unit: MongoExpression[DateUnit],
        amount: MongoExpression[Number],
        timezone: MongoExpression | None = None,
    ) -> DateSubtract:
        return DateSubtract(
            self,
            unit=unit,
            amount=amount,
            timezone=timezone,
        )

    def date_to_parts(
        self,
        *,
        timezone: MongoExpression | None = None,
    ) -> DateToParts:
        return DateToParts(
            self,
            timezone=timezone,
        )

    def date_to_string(
        self,
        *,
        format: str | None = None,
        timezone: MongoExpression | None = None,
        on_null: MongoExpression | None = None,
    ) -> DateToString:
        return DateToString(
            self,
            format=format,
            timezone=timezone,
            on_null=on_null,
        )

    def date_trunc(
        self,
        *,
        unit: MongoExpression[DateUnit],
        bin_size: MongoExpression[Number] | None = None,
        timezone: MongoExpression | None = None,
        start_of_week: MongoExpression[DayWeek] | None = None,
    ) -> DateTrunc:
        return DateTrunc(
            self,
            unit=unit,
            bin_size=bin_size,
            timezone=timezone,
            start_of_week=start_of_week,
        )

    def day_of_month(
        self,
        *,
        timezone: MongoExpression | None = None,
    ) -> DayOfMonth:
        return DayOfMonth(
            self,
            timezone=timezone,
        )

    def day_of_week(
        self,
        *,
        timezone: MongoExpression | None = None,
    ) -> DayOfWeek:
        return DayOfWeek(
            self,
            timezone=timezone,
        )

    def day_of_year(
        self,
        *,
        timezone: MongoExpression | None = None,
    ) -> DayOfYear:
        return DayOfYear(
            self,
            timezone=timezone,
        )

    def degrees_to_radians(self) -> DegreesToRadians:
        return DegreesToRadians(self)

    def exp(self) -> Exp:
        return Exp(self)

    def filter(
        self,
        cond: MongoExpression[Boolean]
        | Callable[[Var, Context], MongoExpression[Boolean]],
        *,
        var: str | None = None,
        limit: MongoExpression[Number] | None = None,
    ) -> Exp:
        return Filter(self, var=var, cond=cond, limit=limit)

    def floor(self) -> Floor:
        return Floor(self)

    def get_field(self, field: str) -> GetField:
        return GetField(input=self, field=field)

    def gt(self, other: MongoExpression) -> Gt:
        return Gt(self, other)

    def gte(self, other: MongoExpression) -> Gte:
        return Gte(self, other)

    def hour(self) -> Hour:
        return Hour(self)

    def in_(self, array: MongoExpression, /) -> IfNull:
        return IfNull(self, array)

    def index_of_array(
        self,
        search: MongoExpression,
        *,
        start: MongoExpression[Number] | None = None,
        end: MongoExpression[Number] | None = None,
    ) -> IndexOfArray:
        return IndexOfArray(
            self,
            search=search,
            start=start,
            end=end,
        )

    def index_of_bytes(
        self,
        search: MongoExpression,
        *,
        start: MongoExpression[Number] | None = None,
        end: MongoExpression[Number] | None = None,
    ) -> IndexOfBytes:
        return IndexOfBytes(
            self,
            search=search,
            start=start,
            end=end,
        )

    def index_of_cp(
        self,
        search: MongoExpression,
        *,
        start: MongoExpression[Number] | None = None,
        end: MongoExpression[Number] | None = None,
    ) -> IndexOfCP:
        return IndexOfCP(
            self,
            search=search,
            start=start,
            end=end,
        )

    def is_array(self) -> IsArray:
        return IsArray(self)

    def is_number(self) -> IsNumber:
        return IsNumber(self)

    def iso_day_of_week(
        self, *, timezone: MongoExpression[Timezone] | None = None
    ) -> IsoDayOfWeek:
        return IsoDayOfWeek(self, timezone=timezone)

    def iso_week_year(
        self, *, timezone: MongoExpression[Timezone] | None = None
    ) -> IsoWeekYear:
        return IsoWeekYear(self, timezone=timezone)

    def ln(self) -> Ln:
        return Ln(self)

    def log(self, base: MongoExpression, /) -> Log10:
        return Log(self, base)

    def log10(self) -> Log10:
        return Log10(self)

    def trim(self, chars: MongoExpression[String]) -> Ltrim:
        return Trim(self, chars=chars)

    def ltrim(self, chars: MongoExpression[String]) -> Ltrim:
        return Ltrim(self, chars=chars)

    def rtrim(self, chars: MongoExpression[String]) -> Rtrim:
        return Rtrim(self, chars=chars)

    def lt(self, other: MongoExpression) -> Lt:
        return Lt(self, other)

    def lte(self, other: MongoExpression) -> Lte:
        return Lte(self, other)

    def map(
        self,
        into: MongoExpression,
        *,
        var: MongoExpression[String] | None = None,
    ) -> Map:
        return Map(self, var=var, into=into)

    def max_n(self, n: MongoExpression[Number], /) -> MaxN:
        return MaxN(self, n=n)

    def min_n(self, n: MongoExpression[Number], /) -> MinN:
        return MinN(self, n=n)

    def millisecond(self) -> Millisecond:
        return Millisecond(self)

    def minute(self) -> Minute:
        return Minute(self)

    def mod(self, other: MongoExpression[Number], /) -> Mod:
        return Mod(self, other)

    def month(self) -> Month:
        return Month(self)

    def multiply(self, *inputs: MongoExpression) -> Multiply:
        return Multiply(self, *inputs)

    def ne(self, other: MongoExpression, /) -> Ne:
        return Ne(self, other)

    def not_(self) -> Not:
        return Not(self)

    def object_to_array(self) -> ObjectToArray:
        return ObjectToArray(self)

    def pow(self, exponent: MongoExpression[Number], /) -> Pow:
        return Pow(self, exponent)

    def radians_to_degrees(self) -> RadiansToDegrees:
        return RadiansToDegrees(self)

    def reduce(
        self,
        into: MongoExpression,
        *,
        initial_value: MongoExpression,
    ) -> Reduce:
        return Reduce(self, into=into, initial_value=initial_value)

    def regex_find(
        self,
        regex: MongoExpression[String],
        *,
        options: MongoExpression[String] | None = None,
    ) -> RegexFind:
        return RegexFind(self, regex=regex, options=options)

    def regex_find_all(
        self,
        regex: MongoExpression[String],
        *,
        options: MongoExpression[String] | None = None,
    ) -> RegexFindAll:
        return RegexFindAll(self, regex=regex, options=options)

    def regex_match(
        self,
        regex: MongoExpression[String],
        *,
        options: MongoExpression[String] | None = None,
    ) -> RegexMatch:
        return RegexMatch(self, regex=regex, options=options)

    def replace_one(
        self,
        find: MongoExpression[String],
        replacement: MongoExpression[String],
    ) -> ReplaceOne:
        return ReplaceOne(
            self,
            find=find,
            replacement=replacement,
        )

    def replace_all(
        self,
        find: MongoExpression[String],
        replacement: MongoExpression[String],
    ) -> ReplaceAll:
        return ReplaceAll(
            self,
            find=find,
            replacement=replacement,
        )

    def reverse_array(self) -> ReverseArray:
        return ReverseArray(self)

    def round(self, place: MongoExpression[Number] = 0, /) -> Round:
        return Round(self, place=place)

    def sample_rate(self) -> SampleRate:
        return SampleRate(self)

    def second(self) -> Second:
        return Second(self)

    def set_difference(self, other: MongoExpression[Array], /) -> SetDifference:
        return SetDifference(self, other)

    def set_equals(self, other: MongoExpression[Array], /) -> SetEquals:
        return SetEquals(self, other)

    def set_intersection(self, other: MongoExpression[Array], /) -> SetIntersection:
        return SetIntersection(self, other)

    def set_is_subset(self, other: MongoExpression[Array], /) -> SetIsSubset:
        return SetIsSubset(self, other)

    def set_union(self, other: MongoExpression[Array], /) -> SetUnion:
        return SetUnion(self, other)

    def set_field(
        self,
        *,
        field: MongoExpression[String],
        value: MongoExpression,
    ) -> SetField:
        return SetField(self, field=field, value=value)

    def sigmoid(
        self,
        *,
        on_null: MongoExpression | None = None,
    ) -> Sigmoid:
        return Sigmoid(self, on_null=on_null)

    def size(self) -> Size:
        return Size(self)

    def sin(self) -> Sin:
        return Sin(self)

    def sinh(self) -> Sinh:
        return Sinh(self)

    def sort_array(self, sort_by: Direction | dict[Field, Direction], /) -> SortArray:
        return SortArray(self, sort_by=sort_by)

    def split(self, delimiter: MongoExpression[String], /) -> Split:
        return Split(self, delimiter=delimiter)

    def sqrt(self) -> Sqrt:
        return Sqrt(self)

    def str_case_cmp(self, other: MongoExpression[String], /) -> StrCaseCmp:
        return StrCaseCmp(self, other)

    def str_len_bytes(self) -> StrLenBytes:
        return StrLenBytes(self)

    def str_len_cp(self) -> StrLenCP:
        return StrLenCP(self)

    def sub_str_bytes(
        self,
        start: MongoExpression[Number],
        length: MongoExpression[Number],
    ) -> SubStrBytes:
        return SubStrBytes(self, start=start, length=length)

    def subtract(
        self,
        other: MongoExpression[String | Number | Date],
    ) -> Subtract:
        return Subtract(self, other)

    def tan(self) -> Tan:
        return Tan(self)

    def tanh(self) -> Tanh:
        return Tanh(self)

    def to_bool(self) -> ToBool:
        return ToBool(self)

    def to_date(self) -> ToDate:
        return ToDate(self)

    def to_decimal(self) -> ToDecimal:
        return ToDecimal(self)

    def to_double(self) -> ToDouble:
        return ToDouble(self)

    def to_hashed_index_key(self) -> ToHashedIndexKey:
        return ToHashedIndexKey(self)

    def to_int(self) -> ToInt:
        return ToInt(self)

    def to_long(self) -> ToLong:
        return ToLong(self)

    def to_object_id(self) -> ToObjectId:
        return ToObjectId(self)

    def to_string(self) -> ToString:
        return ToString(self)

    def to_lower(self) -> ToLower:
        return ToLower(self)

    def to_upper(self) -> ToUpper:
        return ToUpper(self)

    def to_uuid(self) -> ToUUID:
        return ToUUID(self)

    def ts_increment(self) -> TsIncrement:
        return TsIncrement(self)

    def ts_second(self) -> TsSecond:
        return TsSecond(self)

    def trunc(self, place: MongoExpression[Number]) -> Trunc:
        return Trunc(self, place=place)

    def type(self) -> Type:
        return Type(self)

    def unset_field(self, field: MongoExpression[String]) -> UnsetField:
        return UnsetField(input=self, field=field)

    def week(self) -> Week:
        return Week(self)

    def year(self) -> Year:
        return Year(self)

    def zip(
        self,
        *inputs: list[MongoExpression[Array]],
        use_longest_length: bool | None = None,
        defaults: MongoExpression[Array] | None = None,
    ) -> Zip:
        return Zip(
            [self, *inputs],
            use_longest_length=use_longest_length,
            defaults=defaults,
        )


@dataclass(frozen=True)
class Var(
    AsRef, AsAlias, FieldMatcherInterface, FieldSortInterface, FieldUtilInterface
):
    name: str

    def compile_field(self, *, context: Context) -> str:
        return self.name

    def compile_expression(self, *, context: Context) -> str:
        return "$$" + self.name
