"""Described here https://www.mongodb.com/docs/manual/reference/mql/query-predicates/."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, overload

from .compilers import compile_expression, compile_field, compile_query
from .fields import AsField
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
    String,
)
from .types import QueryPredicate as _QueryPredicate
from .utils import nullfree_dict, unwrap_array


class FieldMatcherInterface:
    def all(self, *values: MongoValue | ElemMatch) -> QueryPredicate:
        op = All(*values)
        return FieldMatcher(self, op=op)

    def elem_match(self, *predicates: QueryPredicate | QueryOperator) -> QueryPredicate:
        op = ElemMatch(*predicates)
        return FieldMatcher(self, op=op)

    def size(self, count: Number, /) -> QueryPredicate:
        op = Size(count)
        return FieldMatcher(self, op=op)

    def bits_all_clear(self, bits: Number | Binary | list[Number], /) -> QueryPredicate:
        op = BitsAllClear(bits)
        return FieldMatcher(self, op=op)

    def bits_any_clear(self, bits: Number | Binary | list[Number], /) -> QueryPredicate:
        op = BitsAnyClear(bits)
        return FieldMatcher(self, op=op)

    def bits_all_set(self, bits: Number | Binary | list[Number], /) -> QueryPredicate:
        op = BitsAllSet(bits)
        return FieldMatcher(self, op=op)

    def bits_any_set(self, bits: Number | Binary | list[Number], /) -> QueryPredicate:
        op = BitsAnySet(bits)
        return FieldMatcher(self, op=op)

    def eq(self, value: MongoValue, /) -> QueryPredicate:
        op = Eq(value)
        return FieldMatcher(self, op=op)

    def gt(self, value: MongoValue, /) -> QueryPredicate:
        op = Gt(value)
        return FieldMatcher(self, op=op)

    def gte(self, value: MongoValue, /) -> QueryPredicate:
        op = Gte(value)
        return FieldMatcher(self, op=op)

    def in_(self, *values: MongoValue) -> QueryPredicate:
        op = In(*values)
        return FieldMatcher(self, op=op)

    def lt(self, value: MongoValue, /) -> QueryPredicate:
        op = Lt(value)
        return FieldMatcher(self, op=op)

    def lte(self, value: MongoValue, /) -> QueryPredicate:
        op = Lte(value)
        return FieldMatcher(self, op=op)

    def ne(self, value: MongoValue, /) -> QueryPredicate:
        op = Ne(value)
        return FieldMatcher(self, op=op)

    def nin(self, *values: MongoValue) -> QueryPredicate:
        op = Nin(*values)
        return FieldMatcher(self, op=op)

    def exists(self, value: Boolean, /) -> QueryPredicate:
        op = Exists(value)
        return FieldMatcher(self, op=op)

    def type(self, *types: String) -> QueryPredicate:
        op = Type(*types)
        return FieldMatcher(self, op=op)

    def geo_intersects(self, value: GeoJSON, /) -> QueryPredicate:
        op = GeoIntersects(value)
        return FieldMatcher(self, op=op)

    def geo_within(self, value: GeoJSON, /) -> QueryPredicate:
        op = GeoWithin(value)
        return FieldMatcher(self, op=op)

    def near(
        self,
        value: GeoJSON,
        /,
        min_distance: Number | None = None,
        max_distance: Number | None = None,
    ) -> QueryPredicate:
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
    ) -> QueryPredicate:
        op = NearSphere(
            value,
            min_distance=min_distance,
            max_distance=max_distance,
        )
        return FieldMatcher(self, op=op)

    def mod(self, divisor: Number, remainder: Number) -> QueryPredicate:
        op = Mod(divisor, remainder)
        return FieldMatcher(self, op=op)

    def regex(self, regex: String, *, options: String | None = None) -> QueryPredicate:
        op = Regex(regex, options=options)
        return FieldMatcher(self, op=op)


@dataclass
class Field(AsField, FieldMatcherInterface):
    value: str

    def compile_field(self, *, context: Context) -> str:
        return self.value

    def compile_expression(self, *, context: Context) -> str:
        return "$" + self.value


class QueryPredicate(_QueryPredicate):
    def __and__(self, other: QueryPredicate) -> And:
        return And([self, other])

    def __or__(self, other: QueryPredicate) -> Or:
        return Or([self, other])

    def __invert__(self) -> Not:
        return Not(self)


class QueryOperator(_QueryPredicate):
    pass


@dataclass
class FieldMatcher(QueryPredicate):
    field: str | Field
    op: QueryOperator

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            compile_field(self.field, context=context): compile_query(
                self.op,
                context=context,
            ),
        }


@dataclass
class And(QueryPredicate):
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

    def __and__(self, other: QueryPredicate) -> And:
        return And([*self.predicates, other])


@dataclass
class Nor(QueryPredicate):
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

    def __invert__(self) -> Or:
        return Or(self.predicates)


@dataclass
class Not(QueryPredicate):
    """Selects the documents that do not match the predicate."""

    predicate: QueryOperator | FieldMatcher

    def compile_query(self, context: Context) -> MongoQuery:
        if isinstance(self.predicate, FieldMatcher):
            field = self.predicate.field
            op = self.predicate.op
            return {
                compile_field(field, context=context): {
                    "$not": {compile_query(op, context=context)},
                },
            }
        if isinstance(self.predicate, QueryOperator):
            return {
                "$not": compile_query(self.predicate, context=context),
            }
        raise NotImplementedError

    def __invert__(self) -> MongoQuery:
        return self.predicate


@dataclass
class Or(QueryPredicate):
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

    def __or__(self, other: QueryPredicate) -> Or:
        return Or([*self.predicates, other])

    def __invert__(self) -> Nor:
        return Nor(self.predicates)


@dataclass
class All(QueryOperator):
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
class ElemMatch(QueryOperator):
    """Selects the documents where the value of a field matches all specified values."""

    predicates: list[QueryPredicate | QueryOperator]

    @overload
    def __init__(self, predicate: list[QueryPredicate | QueryOperator], /) -> None: ...

    @overload
    def __init__(self, *predicates: QueryPredicate | QueryOperator) -> None: ...

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
class Size(QueryOperator):
    """Matches any array with the number of elements specified by the argument."""

    count: Number

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$size": self.count,
        }


@dataclass
class BitsAllClear(QueryOperator):
    """Matches documents where all of the bit positions given by the query are clear (i.e. 0) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAllClear": self.bits,
        }


@dataclass
class BitsAllSet(QueryOperator):
    """Matches documents where all of the bit positions given by the query are set (i.e. 1) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAllSet": self.bits,
        }


@dataclass
class BitsAnyClear(QueryOperator):
    """Matches documents where any of the bit positions given by the query are clear (i.e. 0) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAnyClear": self.bits,
        }


@dataclass
class BitsAnySet(QueryOperator):
    """Matches documents where any of the bit positions given by the query are set (i.e. 1) in field."""

    bits: Number | Binary | list[Number]

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$bitsAnySet": self.bits,
        }


@dataclass
class Eq(QueryOperator):
    """Matches documents where the value of a field equals the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$eq": self.value,
        }


@dataclass
class Gt(QueryOperator):
    """Matches documents where the value of the specified field is greater than the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$gt": self.value,
        }


@dataclass
class Gte(QueryOperator):
    """Matches documents where the value of the specified field is greater than or equal to a specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$gte": self.value,
        }


@dataclass
class In(QueryOperator):
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


@dataclass
class Lt(QueryOperator):
    """Matches documents where the value of the specified field is less than the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$lt": self.value,
        }


@dataclass
class Lte(QueryOperator):
    """Matches documents where the value of the specified field is less than or equal to a specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$lte": self.value,
        }


@dataclass
class Ne(QueryOperator):
    """Matches documents where the value of a specified field is not equal to the specified value."""

    value: MongoValue

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$ne": self.value,
        }


@dataclass
class Nin(QueryOperator):
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


@dataclass
class Exists(QueryOperator):
    """Selects the documents where the specified field value is not in the specified array or the specified field does not exist."""

    value: Boolean

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$exists": self.value,
        }


@dataclass
class Type(QueryOperator):
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
class GeoIntersects(QueryOperator):
    """Selects documents whose geospatial data intersects with a specified GeoJSON object; i.e. where the intersection of the data and the specified object is non-empty."""

    value: GeoJSON

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$geoIntersects": compile_geo(self.value, context=context),
        }


@dataclass
class GeoWithin(QueryOperator):
    """Selects documents with geospatial data that exists entirely within a specified shape."""

    value: Geo

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$geoWithin": compile_geo(self.value, context=context),
        }


@dataclass
class Near(QueryOperator):
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
class NearSphere(QueryOperator):
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
class Expr(QueryOperator):
    """Allows the use of expressions within a query predicate."""

    expression: MongoExpression

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$expr": compile_expression(self.expression, context=context),
        }


@dataclass
class JsonSchema(QueryOperator):
    """Matches documents that satisfy the specified JSON Schema."""

    schema: Any

    def compile_query(self, context: Context) -> MongoQuery:
        return {
            "$jsonSchema": compile_expression(self.schema, context=context),
        }


@dataclass
class Mod(QueryOperator):
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
class Regex(QueryOperator):
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
