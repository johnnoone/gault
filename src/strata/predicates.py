"""Described here https://www.mongodb.com/docs/manual/reference/mql/query-predicates/."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, overload

from . import expressions
from .compilers import compile_expression, compile_field, compile_query
from .fields import AsField, FieldSortInterface, FieldUtilInterface
from .geo import Geo, GeoJSON, compile_geo
from .types import (
    Array,
    Binary,
    Boolean,
    Context,
    MongoExpression,
    MongoQuery,
    MongoValue,
    Number,
    QueryPredicate,
    String,
)
from .utils import nullfree_dict, unwrap_array


class FieldMatcherInterface:
    def all(self, *values: MongoValue | ElemMatch) -> Predicate:
        op = All(*values)
        return FieldMatcher(self, op=op)

    def elem_match(self, *predicates: Predicate | Operator) -> Predicate:
        op = ElemMatch(*predicates)
        return FieldMatcher(self, op=op)

    def size(self, count: Number, /) -> Predicate:
        op = Size(count)
        return FieldMatcher(self, op=op)

    def bits_all_clear(self, bits: Number | Binary | list[Number], /) -> Predicate:
        op = BitsAllClear(bits)
        return FieldMatcher(self, op=op)

    def bits_any_clear(self, bits: Number | Binary | list[Number], /) -> Predicate:
        op = BitsAnyClear(bits)
        return FieldMatcher(self, op=op)

    def bits_all_set(self, bits: Number | Binary | list[Number], /) -> Predicate:
        op = BitsAllSet(bits)
        return FieldMatcher(self, op=op)

    def bits_any_set(self, bits: Number | Binary | list[Number], /) -> Predicate:
        op = BitsAnySet(bits)
        return FieldMatcher(self, op=op)

    def eq(self, value: MongoValue, /) -> Predicate:
        op = Eq(value)
        return FieldMatcher(self, op=op)

    def gt(self, value: MongoValue, /) -> Predicate:
        op = Gt(value)
        return FieldMatcher(self, op=op)

    def gte(self, value: MongoValue, /) -> Predicate:
        op = Gte(value)
        return FieldMatcher(self, op=op)

    def in_(self, *values: MongoValue) -> Predicate:
        op = In(*values)
        return FieldMatcher(self, op=op)

    def lt(self, value: MongoValue, /) -> Predicate:
        op = Lt(value)
        return FieldMatcher(self, op=op)

    def lte(self, value: MongoValue, /) -> Predicate:
        op = Lte(value)
        return FieldMatcher(self, op=op)

    def ne(self, value: MongoValue, /) -> Predicate:
        op = Ne(value)
        return FieldMatcher(self, op=op)

    def nin(self, *values: MongoValue) -> Predicate:
        op = Nin(*values)
        return FieldMatcher(self, op=op)

    def exists(self, value: Boolean, /) -> Predicate:
        op = Exists(value)
        return FieldMatcher(self, op=op)

    def type(self, *types: String) -> Predicate:
        op = Type(*types)
        return FieldMatcher(self, op=op)

    def geo_intersects(self, value: GeoJSON, /) -> Predicate:
        op = GeoIntersects(value)
        return FieldMatcher(self, op=op)

    def geo_within(self, value: GeoJSON, /) -> Predicate:
        op = GeoWithin(value)
        return FieldMatcher(self, op=op)

    def near(
        self,
        value: GeoJSON,
        /,
        min_distance: Number | None = None,
        max_distance: Number | None = None,
    ) -> Predicate:
        op = Near(
            value,
            min_distance=min_distance,
            max_distance=max_distance,
        )
        return FieldMatcher(self, op=op)

    def near_sphere(
        self,
        value: GeoJSON,
        /,
        min_distance: Number | None = None,
        max_distance: Number | None = None,
    ) -> Predicate:
        op = NearSphere(
            value,
            min_distance=min_distance,
            max_distance=max_distance,
        )
        return FieldMatcher(self, op=op)

    def mod(self, divisor: Number, remainder: Number) -> Predicate:
        op = Mod(divisor, remainder)
        return FieldMatcher(self, op=op)

    def regex(self, regex: String, *, options: String | None = None) -> Predicate:
        op = Regex(regex, options=options)
        return FieldMatcher(self, op=op)


@dataclass(frozen=True)
class Field(AsField, FieldMatcherInterface, FieldSortInterface, FieldUtilInterface):
    value: str

    def compile_field(self, *, context: Context) -> str:
        return self.value

    def compile_expression(self, *, context: Context) -> str:
        return "$" + self.value


class AsExpression(ABC):
    @abstractmethod
    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        raise NotImplementedError


class Predicate(QueryPredicate):
    def __and__(self, other: Predicate) -> And:
        return And([self, other])

    def __or__(self, other: Predicate) -> Or:
        return Or([self, other])

    def __invert__(self) -> Not:
        return Not(self)


class Operator(QueryPredicate):
    pass


@dataclass
class FieldMatcher(Predicate, expressions.ExpressionOperator):
    field: str | Field
    op: Operator

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            compile_field(self.field, context=context): compile_query(
                self.op,
                context=context,
            ),
        }

    def compile_expression(self, context: Context) -> MongoExpression:
        if isinstance(self.op, AsExpression):
            expression = self.op.as_expression(self.field, context=context)
        else:
            raise NotImplementedError
        return compile_expression(expression, context=context)


@dataclass
class And(Predicate, expressions.ExpressionOperator):
    """Selects the documents that satisfy all the expressions."""

    predicates: list[MongoQuery]

    @overload
    def __init__(self, predicate: list[MongoQuery], /) -> None: ...

    @overload
    def __init__(self, *predicates: MongoQuery) -> None: ...

    def __init__(self, *predicates: Any) -> None:
        self.predicates = unwrap_array(predicates)

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$and": [
                compile_query(predicate, context=context)
                for predicate in self.predicates
            ],
        }

    def compile_expression(self, context: Context) -> MongoExpression:
        return {
            "$and": [
                compile_expression(predicate, context=context)
                for predicate in self.predicates
            ],
        }

    def __and__(self, other: Predicate) -> And:
        return And([*self.predicates, other])


@dataclass
class Nor(Predicate):
    """Selects the documents that fail all the query predicates in the array."""

    predicates: list[MongoQuery]

    @overload
    def __init__(self, predicate: list[MongoQuery], /) -> None: ...

    @overload
    def __init__(self, *predicates: MongoQuery) -> None: ...

    def __init__(self, *predicates: Any) -> None:
        self.predicates = unwrap_array(predicates)

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$nor": [
                compile_query(predicate, context=context)
                for predicate in self.predicates
            ],
        }

    def compile_expression(self, context: Context) -> MongoExpression:
        return expressions.Not(
            {
                "$or": [
                    compile_expression(predicate, context=context)
                    for predicate in self.predicates
                ],
            },
        ).compile_expression(context=context)

    def __invert__(self) -> Or:
        return Or(self.predicates)


@dataclass
class Not(Predicate):
    """Selects the documents that do not match the predicate."""

    predicate: Operator | FieldMatcher

    def compile_query(self, context: Context) -> MongoQuery:
        if isinstance(self.predicate, FieldMatcher):
            field = self.predicate.field
            op = self.predicate.op
            return {
                compile_field(field, context=context): {
                    "$not": {compile_query(op, context=context)},
                },
            }
        if isinstance(self.predicate, Operator):
            return {
                "$not": compile_query(self.predicate, context=context),
            }
        raise NotImplementedError

    def compile_expression(self, context: Context) -> MongoExpression:
        return Not(
            compile_expression(self.predicate, context=context),
        ).compile_expression(context=context)

    def __invert__(self) -> MongoQuery:
        return self.predicate


@dataclass
class Or(Predicate):
    """Selects the documents that satisfy at least one of the predicates."""

    predicates: list[MongoQuery]

    @overload
    def __init__(self, predicate: list[MongoQuery], /) -> None: ...

    @overload
    def __init__(self, *predicates: MongoQuery) -> None: ...

    def __init__(self, *predicates: Any) -> None:
        self.predicates = unwrap_array(predicates)

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$or": [
                compile_query(predicate, context=context)
                for predicate in self.predicates
            ],
        }

    def compile_expression(self, context: Context) -> MongoExpression:
        return {
            "$or": [
                compile_expression(predicate, context=context)
                for predicate in self.predicates
            ],
        }

    def __or__(self, other: Predicate) -> Or:
        return Or([*self.predicates, other])

    def __invert__(self) -> Nor:
        return Nor(self.predicates)


@dataclass
class All(Operator):
    """Selects the documents where the value of a field matches all specified values."""

    values: list[MongoValue | ElemMatch]

    @overload
    def __init__(self, value: list[MongoValue | ElemMatch], /) -> None: ...

    @overload
    def __init__(self, *values: MongoValue | ElemMatch) -> None: ...

    def __init__(self, *values: Any) -> None:
        self.values = unwrap_array(values)

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$all": [compile_query(value, context=context) for value in self.values],
        }


@dataclass
class ElemMatch(Operator):
    """Selects the documents where the value of a field matches all specified values."""

    predicates: list[Predicate | Operator]

    @overload
    def __init__(self, predicate: list[Predicate | Operator], /) -> None: ...

    @overload
    def __init__(self, *predicates: Predicate | Operator) -> None: ...

    def __init__(self, *predicates: Any) -> None:
        self.predicates = unwrap_array(predicates)

    def compile_query(self, context: Context) -> MongoQuery:
        query = {}
        for predicate in self.predicates:
            query |= compile_query(predicate, context=context)

        return {
            "$elemMatch": query,
        }


@dataclass
class Size(Operator, AsExpression):
    """Matches any array with the number of elements specified by the argument."""

    count: Number

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$size": self.count,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.Eq(expressions.Size(field), self.value)


@dataclass
class BitsAllClear(Operator):
    """Matches documents where all of the bit positions given by the query are clear (i.e. 0) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAllClear": self.bits,
        }


@dataclass
class BitsAllSet(Operator):
    """Matches documents where all of the bit positions given by the query are set (i.e. 1) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAllSet": self.bits,
        }


@dataclass
class BitsAnyClear(Operator):
    """Matches documents where any of the bit positions given by the query are clear (i.e. 0) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAnyClear": self.bits,
        }


@dataclass
class BitsAnySet(Operator):
    """Matches documents where any of the bit positions given by the query are set (i.e. 1) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAnySet": self.bits,
        }


@dataclass
class Eq(Operator, AsExpression):
    """Matches documents where the value of a field equals the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$eq": self.value,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.Eq(field, self.value)


@dataclass
class Gt(Operator):
    """Matches documents where the value of the specified field is greater than the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$gt": self.value,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.Gt(field, self.value)


@dataclass
class Gte(Operator, AsExpression):
    """Matches documents where the value of the specified field is greater than or equal to a specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$gte": self.value,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.Gte(field, self.value)


@dataclass
class In(Operator, AsExpression):
    """Selects the documents where the value of a field equals any value in the specified array."""

    values: list[MongoValue]

    @overload
    def __init__(self, value: list[MongoValue], /) -> None: ...

    @overload
    def __init__(self, *values: MongoValue) -> None: ...

    def __init__(self, *values: Any) -> None:
        self.values = unwrap_array(values)

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$in": self.values,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.In(field, self.value)


@dataclass
class Lt(Operator, AsExpression):
    """Matches documents where the value of the specified field is less than the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$lt": self.value,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.Lt(field, self.value)


@dataclass
class Lte(Operator, AsExpression):
    """Matches documents where the value of the specified field is less than or equal to a specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$lte": self.value,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.Lte(field, self.value)


@dataclass
class Ne(Operator, AsExpression):
    """Matches documents where the value of a specified field is not equal to the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$ne": compile_expression(self.value, context=context),
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.Ne(field, self.value)


@dataclass
class Nin(Operator, AsExpression):
    """Selects the documents where the specified field value is not in the specified array or the specified field does not exist."""

    values: list[MongoValue]

    @overload
    def __init__(self, value: list[MongoValue], /) -> None: ...

    @overload
    def __init__(self, *values: MongoValue) -> None: ...

    def __init__(self, *values: Any) -> None:
        self.values = unwrap_array(values)

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$nin": self.values,
        }

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return ~expressions.In(field, self.value)


@dataclass
class Exists(Operator):
    """Selects the documents where the specified field value is not in the specified array or the specified field does not exist."""

    value: Boolean

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$exists": self.value,
        }


@dataclass
class Type(Operator):
    """Selects documents where the value of the field is an instance of the specified BSON type(s)."""

    types: Array[String] | String

    @overload
    def __init__(self, type: Array[String], /) -> None: ...

    @overload
    def __init__(self, *types: String) -> None: ...

    def __init__(self, *types: Any) -> None:
        self.types = unwrap_array(types)

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$type": self.types,
        }


@dataclass
class GeoIntersects(Operator):
    """Selects documents whose geospatial data intersects with a specified GeoJSON object; i.e. where the intersection of the data and the specified object is non-empty."""

    value: GeoJSON

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$geoIntersects": compile_geo(self.value, context=context),
        }


@dataclass
class GeoWithin(Operator):
    """Selects documents with geospatial data that exists entirely within a specified shape."""

    value: Geo

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$geoWithin": compile_geo(self.value, context=context),
        }


@dataclass
class Near(Operator):
    """Specifies a point for which a geospatial query returns the documents from nearest to farthest."""

    value: Geo
    min_distance: Number | None = None
    max_distance: Number | None = None

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$near": compile_geo(self.value, context=context),
        } | nullfree_dict(
            {
                "$minDistance": self.min_distance,
                "$maxDistance": self.max_distance,
            },
        )


@dataclass
class NearSphere(Operator):
    """Specifies a point for which a geospatial query returns the documents from nearest to farthest."""

    value: Geo
    min_distance: Number | None = None
    max_distance: Number | None = None

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$nearSphere": compile_geo(self.value, context=context),
        } | nullfree_dict(
            {
                "$minDistance": self.min_distance,
                "$maxDistance": self.max_distance,
            },
        )


@dataclass
class Expr(Operator):
    """Allows the use of expressions within a query predicate."""

    expression: MongoExpression

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$expr": compile_expression(self.expression, context=context),
        }


@dataclass
class JsonSchema(Operator):
    """Matches documents that satisfy the specified JSON Schema."""

    schema: Any

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$jsonSchema": compile_expression(self.schema, context=context),
        }


@dataclass
class Mod(Operator):
    """Matches documents that satisfy the specified JSON Schema."""

    divisor: Number
    remainder: Number

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$mod": [
                compile_expression(self.divisor, context=context),
                compile_expression(self.remainder, context=context),
            ],
        }


@dataclass
class Regex(Operator, AsExpression):
    """Matches documents that satisfy the specified JSON Schema."""

    regex: String
    options: String | None = None

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$regex": compile_expression(self.regex, context=context),
        } | nullfree_dict(
            {
                "$options": compile_expression(self.options, context=context),
            },
        )

    def as_expression(
        self,
        field: Field,
        context: Context,
    ) -> expressions.ExpressionOperator:
        return expressions.RegexMatch(field, regex=self.regex, options=self.options)
