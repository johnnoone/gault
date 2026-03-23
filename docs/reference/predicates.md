# Predicates

Query predicates for building MongoDB query filters. All predicate classes live in `gault.predicates`. Predicates compile to MongoDB query documents via `compile_query()`.

```python
from gault import Field, Query
from gault.predicates import And, Or, Nor, Not, Eq, Gt, Gte, Lt, Lte, Ne, In, Nin
```

## Field

```python
@dataclass(frozen=True)
class Field(AsRef, ConditionInterface, FieldSortInterface, SubfieldInterface,
            NotInterface, ExpressionInterface, InclusionInterface, Assignable)
```

A field reference for building predicates, sort tokens, and expressions. This is the primary entry point for constructing queries.

### Constructor

```python
Field(name: str)
```

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | The MongoDB field name. |

### Predicate methods (ConditionInterface)

All methods return a `Predicate` object.

| Method | Signature | MongoDB operator | Description |
|---|---|---|---|
| `eq()` | `eq(value)` | `$eq` | Equals |
| `ne()` | `ne(value)` | `$ne` | Not equals |
| `gt()` | `gt(value)` | `$gt` | Greater than |
| `gte()` | `gte(value)` | `$gte` | Greater than or equal |
| `lt()` | `lt(value)` | `$lt` | Less than |
| `lte()` | `lte(value)` | `$lte` | Less than or equal |
| `in_()` | `in_(*values)` | `$in` | Value in array |
| `nin()` | `nin(*values)` | `$nin` | Value not in array |
| `exists()` | `exists(bool)` | `$exists` | Field exists |
| `type()` | `type(*types)` | `$type` | BSON type check |
| `regex()` | `regex(pattern, *, options=None)` | `$regex` | Regular expression match |
| `mod()` | `mod(divisor, remainder)` | `$mod` | Modulo operation |
| `all()` | `all(*values)` | `$all` | Array contains all values |
| `elem_match()` | `elem_match(*predicates)` | `$elemMatch` | Array element match |
| `size()` | `size(count)` | `$size` | Array size |
| `bits_all_clear()` | `bits_all_clear(bits)` | `$bitsAllClear` | Bitwise all clear |
| `bits_any_clear()` | `bits_any_clear(bits)` | `$bitsAnyClear` | Bitwise any clear |
| `bits_all_set()` | `bits_all_set(bits)` | `$bitsAllSet` | Bitwise all set |
| `bits_any_set()` | `bits_any_set(bits)` | `$bitsAnySet` | Bitwise any set |
| `geo_intersects()` | `geo_intersects(geometry)` | `$geoIntersects` | Geospatial intersection |
| `geo_within()` | `geo_within(geometry)` | `$geoWithin` | Geospatial containment |
| `near()` | `near(point, min_distance=None, max_distance=None)` | `$near` | Proximity query |
| `near_sphere()` | `near_sphere(point, min_distance=None, max_distance=None)` | `$nearSphere` | Spherical proximity |

### Sorting methods (FieldSortInterface)

| Method | Signature | Returns | Description |
|---|---|---|---|
| `asc()` | `asc()` | `tuple[Self, 1]` | Ascending sort token |
| `desc()` | `desc()` | `tuple[Self, -1]` | Descending sort token |
| `by_score()` | `by_score(name)` | `tuple[Self, {"$meta": name}]` | Sort by text score |

### Subfield access (SubfieldInterface)

```python
Field("address").field("city")
# Represents "address.city"
```

### Negation (NotInterface)

The `not_` property returns a `NotProxy` that wraps any subsequent operator with `$not`:

```python
Field("age").not_.gte(18)
# {"age": {"$not": {"$gte": 18}}}
```

### Expression proxy (ExpressionInterface)

The `expr` property returns an `ExpressionProxy` for use in `$expr` queries:

```python
Field("score").expr.gt(42)
# Used in: Pipeline().match(Field("score").expr.gt(42))
# Compiles to: {"$expr": {"$gt": ["$score", 42]}}
```

### Projection methods (InclusionInterface)

| Method | Signature | Description |
|---|---|---|
| `keep()` | `keep(*, alias=None)` | Include this field in projection. If `alias` is given, project under a different name. |
| `remove()` | `remove()` | Exclude this field (`"$$REMOVE"`). |

```python
Field("name").keep()                    # Aliased("name", True)
Field("name").keep(alias="full_name")   # Aliased("full_name", Field("name"))
Field("internal").remove()              # Aliased("internal", "$$REMOVE")
```

### Assignment (Assignable)

```python
Field("status").assign("active")
# Aliased(Field("status"), "active")
# Used in: Pipeline().set(Field("status").assign("active"))
```

### Temporary fields (TempFieldInterface)

```python
Field.tmp()
# Creates a Field with a random name like "__64a1b2c3..."
# Useful for intermediate pipeline computations
```

### Example

```python
from gault import Field, Pipeline

f = Field("age")

# Build predicates
predicate = f.gte(18) & f.lt(65)

# Use in pipeline
Pipeline().match(predicate)

# Sort
Pipeline().sort(f.desc())

# Project
Pipeline().project(f.keep(), Field("name").keep())
```

---

## Query

```python
def Query() -> Predicate
```

Creates a no-op predicate (`NoOp`) that matches all documents. Useful as a starting point for building queries with `&` and `|`:

```python
from gault import Query, Field

q = Query()
q = q & Field("age").gte(18)
q = q & Field("status").eq("active")
```

`NoOp` is transparent -- `NoOp() & predicate` returns `predicate`, and `NoOp() | predicate` returns `predicate`.

---

## Predicate

```python
class Predicate(QueryPredicate)
```

Base class for all query predicates. Supports combining with Python operators:

| Operator | Result | Description |
|---|---|---|
| `pred1 & pred2` | `And([pred1, pred2])` | Logical AND |
| `pred1 \| pred2` | `Or([pred1, pred2])` | Logical OR |

---

## Comparison operators

### Eq

```python
@dataclass
class Eq(Operator, AsExpression)
```

Matches documents where the field equals the specified value.

| Parameter | Type | Description |
|---|---|---|
| `value` | `Value` | Value to compare against. |

```python
Field("status").eq("active")
# Compiles to: {"status": {"$eq": "active"}}
```

### Ne

```python
@dataclass
class Ne(Operator, AsExpression)
```

Matches documents where the field does not equal the specified value.

| Parameter | Type | Description |
|---|---|---|
| `value` | `AsRef \| Value` | Value to compare against. Can be a field reference. |

```python
Field("status").ne("deleted")
# {"status": {"$ne": "deleted"}}
```

### Gt

```python
@dataclass
class Gt(Operator, AsExpression)
```

Matches documents where the field is greater than the value.

| Parameter | Type | Description |
|---|---|---|
| `value` | `PathLike \| Value` | Value or field reference. |

```python
Field("age").gt(18)
# {"age": {"$gt": 18}}
```

### Gte

```python
@dataclass
class Gte(Operator, AsExpression)
```

Matches documents where the field is greater than or equal to the value.

| Parameter | Type | Description |
|---|---|---|
| `value` | `PathLike \| Value` | Value or field reference. |

```python
Field("age").gte(18)
# {"age": {"$gte": 18}}
```

### Lt

```python
@dataclass
class Lt(Operator, AsExpression)
```

Matches documents where the field is less than the value.

| Parameter | Type | Description |
|---|---|---|
| `value` | `PathLike \| Value` | Value or field reference. |

```python
Field("age").lt(65)
# {"age": {"$lt": 65}}
```

### Lte

```python
@dataclass
class Lte(Operator, AsExpression)
```

Matches documents where the field is less than or equal to the value.

| Parameter | Type | Description |
|---|---|---|
| `value` | `PathLike \| Value` | Value or field reference. |

```python
Field("score").lte(100)
# {"score": {"$lte": 100}}
```

### In

```python
@dataclass
class In(Operator, AsExpression)
```

Matches documents where the field value is in the specified array.

| Parameter | Type | Description |
|---|---|---|
| `*values` | `Value` | Values to match against. Also accepts a single list. |

```python
Field("status").in_("active", "pending")
# {"status": {"$in": ["active", "pending"]}}

Field("status").in_(["active", "pending"])
# {"status": {"$in": ["active", "pending"]}}
```

### Nin

```python
@dataclass
class Nin(Operator, AsExpression)
```

Matches documents where the field value is NOT in the specified array, or the field does not exist.

| Parameter | Type | Description |
|---|---|---|
| `*values` | `Value` | Values to exclude. Also accepts a single list. |

```python
Field("status").nin("deleted", "archived")
# {"status": {"$nin": ["deleted", "archived"]}}
```

---

## Logical operators

### And

```python
@dataclass
class And(Predicate, ExpressionOperator)
```

Matches documents that satisfy ALL predicates.

| Parameter | Type | Description |
|---|---|---|
| `*predicates` | `Predicate \| MongoQuery` | Predicates to combine. Also accepts a single list. |

```python
And(Field("age").gte(18), Field("status").eq("active"))
# {"$and": [{"age": {"$gte": 18}}, {"status": {"$eq": "active"}}]}
```

Chaining with `&` appends to the existing list:

```python
pred = Field("a").eq(1) & Field("b").eq(2) & Field("c").eq(3)
# And([a==1, b==2, c==3]) -- flat, not nested
```

### Or

```python
@dataclass
class Or(Predicate, ExpressionOperator)
```

Matches documents that satisfy at least one predicate.

| Parameter | Type | Description |
|---|---|---|
| `*predicates` | `Predicate \| MongoQuery` | Predicates to combine. Also accepts a single list. |

```python
Or(Field("status").eq("active"), Field("status").eq("pending"))
# {"$or": [{"status": {"$eq": "active"}}, {"status": {"$eq": "pending"}}]}
```

Chaining with `|` appends:

```python
pred = Field("a").eq(1) | Field("b").eq(2) | Field("c").eq(3)
# Or([a==1, b==2, c==3])
```

Inverting an `Or` produces a `Nor`:

```python
~Or(Field("a").eq(1), Field("b").eq(2))
# Nor([a==1, b==2])
```

### Nor

```python
@dataclass
class Nor(Predicate)
```

Matches documents that fail ALL predicates.

| Parameter | Type | Description |
|---|---|---|
| `*predicates` | `Predicate \| MongoQuery` | Predicates. Also accepts a single list. |

```python
Nor(Field("status").eq("deleted"), Field("age").lt(18))
# {"$nor": [{"status": {"$eq": "deleted"}}, {"age": {"$lt": 18}}]}
```

Inverting a `Nor` produces an `Or`:

```python
~Nor(Field("a").eq(1), Field("b").eq(2))
# Or([a==1, b==2])
```

### Not

```python
@dataclass
class Not(Operator)
```

Negates a single operator. Used as a field-level operator (different from `Nor` which is top-level).

| Parameter | Type | Description |
|---|---|---|
| `operator` | `Operator \| Value` | The operator to negate. |

```python
# Via not_ property
Field("age").not_.gte(18)
# {"age": {"$not": {"$gte": 18}}}

# Direct instantiation
from gault.predicates import Not, Gte
Not(Gte(18))
# {"$not": {"$gte": 18}}
```

Operators can also be inverted with `~`:

```python
~Gte(18)   # Not(Gte(18))
```

---

## Array operators

### All

```python
@dataclass
class All(Operator)
```

Matches documents where the array field contains all specified values.

| Parameter | Type | Description |
|---|---|---|
| `*values` | `Value \| ElemMatch` | Values the array must contain. Also accepts a single list. |

```python
Field("tags").all("python", "mongodb")
# {"tags": {"$all": ["python", "mongodb"]}}
```

### ElemMatch

```python
@dataclass
class ElemMatch(Operator)
```

Matches documents where at least one array element satisfies all specified conditions.

| Parameter | Type | Description |
|---|---|---|
| `*predicates` | `Predicate \| Operator \| Object` | Conditions to apply to elements. Also accepts a single list. |

```python
Field("scores").elem_match(Field("value").gte(80), Field("type").eq("exam"))
# {"scores": {"$elemMatch": {"value": {"$gte": 80}, "type": {"$eq": "exam"}}}}
```

`ElemMatch` can also be used within `All`:

```python
Field("results").all(
    ElemMatch(Gte(80)),
    ElemMatch(Lt(90)),
)
```

### Size

```python
@dataclass
class Size(Operator, AsExpression)
```

Matches arrays with the specified number of elements.

| Parameter | Type | Description |
|---|---|---|
| `count` | `Number` | Expected array length. |

```python
Field("tags").size(3)
# {"tags": {"$size": 3}}
```

---

## Regex

```python
@dataclass
class Regex(Operator, AsExpression)
```

Matches documents using a regular expression.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `regex` | `String` | _(required)_ | The regex pattern. |
| `options` | `String \| None` | `None` | Regex options: `"i"` (case-insensitive), `"m"` (multiline), `"x"` (extended), `"s"` (dotall). |

```python
Field("name").regex("^Alice", options="i")
# {"name": {"$regex": "^Alice", "$options": "i"}}
```

---

## Exists

```python
@dataclass
class Exists(Operator)
```

Matches documents where the field exists (or does not exist).

| Parameter | Type | Description |
|---|---|---|
| `value` | `Boolean` | `True` to match existing fields, `False` to match missing fields. |

```python
Field("email").exists(True)
# {"email": {"$exists": true}}

Field("deleted_at").exists(False)
# {"deleted_at": {"$exists": false}}
```

---

## Type

```python
@dataclass
class Type(Operator)
```

Matches documents where the field value is of the specified BSON type(s).

| Parameter | Type | Description |
|---|---|---|
| `*types` | `String \| Number` | BSON type name(s) or number(s). Also accepts a single list. |

Valid string types: `"double"`, `"string"`, `"object"`, `"array"`, `"binData"`, `"objectId"`, `"bool"`, `"date"`, `"null"`, `"regex"`, `"int"`, `"timestamp"`, `"long"`, `"decimal"`, `"number"`, etc.

```python
Field("value").type("string", "int")
# {"value": {"$type": ["string", "int"]}}
```

---

## Expr

```python
@dataclass
class Expr(Operator, ExpressionOperator)
```

Allows use of aggregation expressions within a query predicate.

| Parameter | Type | Description |
|---|---|---|
| `expression` | `AnyExpression` | An aggregation expression. |

```python
from gault.predicates import Expr
from gault.expressions import Gt

Expr(Gt("$spent", "$budget"))
# {"$expr": {"$gt": ["$spent", "$budget"]}}
```

---

## Raw

```python
@dataclass
class Raw(Predicate)
```

A pass-through for raw MongoDB query documents.

| Parameter | Type | Description |
|---|---|---|
| `query` | `MongoQuery` | A raw MongoDB query dict. |

```python
from gault.predicates import Raw

Raw({"$text": {"$search": "coffee shop"}})
# {"$text": {"$search": "coffee shop"}}
```

---

## Combining predicates

Predicates support Python operators for composition:

```python
# AND
p = Field("age").gte(18) & Field("status").eq("active")

# OR
p = Field("role").eq("admin") | Field("role").eq("moderator")

# Complex
p = (Field("age").gte(18) & Field("status").eq("active")) | Field("role").eq("admin")
```

These compile to nested `$and` / `$or` structures as expected by MongoDB.

---

## Compile output examples

```python
# Simple equality
Field("name").eq("Alice")
# {"name": {"$eq": "Alice"}}

# Range query
Field("age").gte(18) & Field("age").lt(65)
# {"$and": [{"age": {"$gte": 18}}, {"age": {"$lt": 65}}]}

# OR query
Field("status").in_("active", "pending")
# {"status": {"$in": ["active", "pending"]}}

# NOT with regex
Field("name").not_.regex("^test", options="i")
# {"name": {"$not": {"$regex": "^test", "$options": "i"}}}

# Nested field
Field("address").field("city").eq("Paris")
# {"address.city": {"$eq": "Paris"}}

# Array elem_match
Field("scores").elem_match(Gte(80), Lt(100))
# {"scores": {"$elemMatch": {"$gte": 80, "$lt": 100}}}
```
