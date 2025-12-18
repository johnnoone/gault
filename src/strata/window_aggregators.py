from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .compilers import compile_field

from .expressions import (
    Array,
    Context,
    DateUnit,
    MongoExpression,
    Number,
    compile_expression,
)


class WindowOperator(ABC):
    """Described here https://www.mongodb.com/docs/manual/reference/mql/expressions/."""

    @abstractmethod
    def compile_expression(self, context: Context) -> MongoExpression:
        raise NotImplementedError


@dataclass
class CovariancePop(WindowOperator):
    """Returns the population covariance of two numeric expressions that are evaluated using documents in the `$setWindowFields` stage window."""

    value1: MongoExpression[Number]
    """any valid expression that resolves to a number, measured in radians"""

    value2: MongoExpression[Number]
    """any valid expression that resolves to a number, measured in radians"""

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$covariancePop": [
                compile_expression(self.value1, context=context),
                compile_expression(self.value2, context=context),
            ],
        }


@dataclass
class CovarianceSamp(WindowOperator):
    """Returns the sample covariance of two numeric expressions that are evaluated using documents in the `$setWindowFields` stage window."""

    value1: MongoExpression[Number]
    """any valid expression that resolves to a number, measured in radians"""

    value2: MongoExpression[Number]
    """any valid expression that resolves to a number, measured in radians"""

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$covarianceSamp": [
                compile_expression(self.value1, context=context),
                compile_expression(self.value2, context=context),
            ],
        }


@dataclass
class DenseRank(WindowOperator):
    """Returns the document position (known as the rank) relative to other documents in the $setWindowFields stage partition."""

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {"$denseRank": {}}


@dataclass
class Derivative(WindowOperator):
    """Returns the average rate of change within the specified window."""

    input: MongoExpression[Number]
    """any valid expression that resolves to a number.
    """

    unit: MongoExpression[DateUnit]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$derivative": {
                "input": compile_expression(self.input, context=context),
                "unit": compile_expression(self.unit, context=context),
            },
        }


@dataclass
class DocumentNumber(WindowOperator):
    """Returns the position of a document (known as the document number) in the $setWindowFields stage partition."""

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {"$documentNumber": {}}


@dataclass
class ExpMovingAvg(WindowOperator):
    """Returns the exponential moving average of numeric expressions applied to documents in a partition defined in the $setWindowFields stage."""

    input: MongoExpression
    """any valid expression as long as it resolves to a number"""

    n: MongoExpression
    """any valid expression as long as it resolves to a number"""

    alpha: MongoExpression
    """any valid expression as long as it resolves to a number"""

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$expMovingAvg": {
                "input": compile_expression(self.input, context=context),
                "N": compile_expression(self.n, context=context),
                "alpha": compile_expression(self.alpha, context=context),
            },
        }


@dataclass
class Integral(WindowOperator):
    """Returns the approximation of the area under a curve."""

    input: MongoExpression[Number]
    """an expression that returns a number."""

    unit: MongoExpression[DateUnit]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$integral": {
                "input": compile_expression(self.input, context=context),
                "unit": compile_expression(self.unit, context=context),
            },
        }


@dataclass
class LinearFill(WindowOperator):
    """Fills null and missing fields in a window using linear interpolation based on surrounding field values."""

    input: MongoExpression
    """The expression to evaluate."""

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$linearFill": compile_expression(self.into, context=context),
        }


@dataclass
class Locf(WindowOperator):
    """Last observation carried forward."""

    input: MongoExpression
    """Any valid expression"""

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {"$locf": compile_expression(self.input, context=context)}


@dataclass
class MinMaxScaler(WindowOperator):
    """Normalizes a numeric expression within a window of values."""

    input: MongoExpression[Number]
    """An expression that resolves to the array"""

    min: MongoExpression[Number] = 0
    """An expression that resolves to a positive integer"""

    max: MongoExpression[Number] = 1
    """An expression that resolves to a positive integer"""

    def compile_expression(self, *, context: Context) -> MongoExpression[Array]:
        return {
            "$minMaxScaler": {
                "input": compile_expression(self.input, context=context),
                "min": compile_field(self.min, context=context),
                "max": compile_field(self.max, context=context),
            },
        }


@dataclass
class Rank(WindowOperator):
    """Returns the document position (known as the rank) relative to other documents in the $setWindowFields stage partition."""

    def compile_expression(self, *, context: Context) -> MongoExpression[Number]:
        return {
            "$rank": {},
        }


@dataclass
class Shift(WindowOperator):
    """Returns the value from an expression applied to a document in a specified position relative to the current document in the $setWindowFields stage partition."""

    output: MongoExpression
    by: MongoExpression[Number]
    default: MongoExpression

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$shift": {
                "output": compile_expression(self.output, context=context),
                "by": compile_expression(self.by, context=context),
                "default": compile_expression(self.default, context=context),
            },
        }
