# Pipeline

The `Pipeline` class provides a fluent, immutable builder for MongoDB aggregation pipelines. Every method returns a new `Pipeline` instance (the original is never mutated).

## Pipeline

```python
@dataclass
class Pipeline(AsAlias)
```

### Constructor

```python
Pipeline(*, steps: list[Step] = [])
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `steps` | `list[Step]` | `[]` | Internal list of pipeline steps. Normally you do not pass this directly. |

---

### match()

```python
def match(self, *predicates: MongoQuery | Predicate) -> Self
```

Add a `$match` stage. Filters documents matching the specified condition(s). Multiple predicates are combined with `$and`.

| Parameter | Type | Description |
|---|---|---|
| `*predicates` | `MongoQuery \| Predicate` | One or more predicates or raw query dicts. Also accepts a single `list`. |

**Returns:** `Self` (new Pipeline)

```python
# Raw dict
Pipeline().match({"status": "active"})

# Predicate
Pipeline().match(Field("age").gte(18))

# Multiple predicates (AND)
Pipeline().match(Field("status").eq("active"), Field("age").gte(18))

# Combined with &
Pipeline().match(Field("status").eq("active") & Field("age").gte(18))
```

**Compiles to:**
```json
[{"$match": {"status": {"$eq": "active"}, "age": {"$gte": 18}}}]
```

---

### sort()

```python
def sort(self, *spec: SortPayload) -> Self
```

Add a `$sort` stage. Reorders documents by the specified key(s).

| Parameter | Type | Description |
|---|---|---|
| `*spec` | `SortPayload` | Sort specification: `SortToken`, `list[SortToken]`, or `dict`. Passing `None` is a no-op. |

**Returns:** `Self`

```python
# String field name (ascending by default)
Pipeline().sort("name")

# AttributeSpec tokens
Pipeline().sort(User.age.desc(), User.name.asc())

# Dict
Pipeline().sort({"age": -1, "name": 1})

# List of tokens
Pipeline().sort([User.age.desc(), User.name.asc()])
```

**Compiles to:**
```json
[{"$sort": {"age": -1, "name": 1}}]
```

---

### skip()

```python
def skip(self, size: PositiveInteger | None, /) -> Self
```

Add a `$skip` stage. Skips the first `n` documents. Passing `None` is a no-op.

| Parameter | Type | Description |
|---|---|---|
| `size` | `int \| None` | Number of documents to skip. |

**Returns:** `Self`

```python
Pipeline().skip(20)
```

**Compiles to:**
```json
[{"$skip": 20}]
```

---

### take()

```python
def take(self, size: PositiveInteger | None, /) -> Self
```

Add a `$limit` stage. Limits the number of documents. Passing `None` is a no-op.

| Parameter | Type | Description |
|---|---|---|
| `size` | `int \| None` | Maximum number of documents. |

**Returns:** `Self`

```python
Pipeline().skip(20).take(10)
```

**Compiles to:**
```json
[{"$skip": 20}, {"$limit": 10}]
```

---

### project()

```python
def project(self, *projection: type[Model] | list[Aliased] | Mapping | Aliased) -> Self
```

Add a `$project` stage. Reshapes documents by including, excluding, or computing fields.

| Parameter | Type | Description |
|---|---|---|
| `*projection` | `type[Model]`, `dict`, `list[Aliased]`, or spread `Aliased` | Projection specification. |

**Returns:** `Self`

```python
# Project to a Model (includes only that model's fields)
Pipeline().project(UserSummary)

# Project with dict
Pipeline().project({"name": True, "age": True})

# Project with Field keep/remove
Pipeline().project(
    Field("name").keep(),
    Field("age").keep(alias="person_age"),
    Field("internal").remove(),
)

# Project with list
Pipeline().project([Field("name").keep(), Field("age").keep()])
```

When projecting with a `Model` class, `_id` is excluded and all model fields are included:

**Compiles to:**
```json
[{"$project": {"_id": false, "name": true, "email": true}}]
```

---

### group()

```python
def group(self, *accumulators: Aliased | dict | list | None, by: AnyExpression) -> Self
```

Add a `$group` stage. Groups documents by an expression and applies accumulators.

| Parameter | Type | Description |
|---|---|---|
| `*accumulators` | `dict`, `list[Aliased]`, or spread `Aliased` | Accumulator definitions. Pass `None` for group-only (no accumulators). |
| `by` | `AnyExpression` | Group key expression. Use `None` to group all documents together. |

**Returns:** `Self`

```python
from gault.accumulators import Sum, Avg, Count

# Dict form
Pipeline().group(
    {"total": Sum("$amount"), "avg": Avg("$score")},
    by="$category",
)

# Spread Aliased form
Pipeline().group(
    Sum("$amount").alias("total"),
    Avg("$score").alias("avg"),
    by="$category",
)

# Group all documents
Pipeline().group({"count": Count()}, by=None)
```

**Compiles to:**
```json
[{"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "avg": {"$avg": "$score"}}}]
```

---

### set()

```python
def set(self, *fields: Mapping | list[Aliased] | Aliased) -> Self
```

Add a `$set` stage. Adds new fields or replaces existing ones.

| Parameter | Type | Description |
|---|---|---|
| `*fields` | `dict`, `list[Aliased]`, or spread `Aliased` | Field definitions. |

**Returns:** `Self`

```python
# Dict form
Pipeline().set({"total": {"$multiply": ["$price", "$qty"]}, "status": "done"})

# Spread Aliased form
Pipeline().set(
    Field("total").assign({"$multiply": ["$price", "$qty"]}),
    Field("status").assign("done"),
)
```

**Compiles to:**
```json
[{"$set": {"total": {"$multiply": ["$price", "$qty"]}, "status": "done"}}]
```

---

### set_field()

```python
def set_field(self, field: FieldLike, value: AnyExpression, /) -> Self
```

Convenience method to set a single field. Calls `self.set({field: value})` internally.

| Parameter | Type | Description |
|---|---|---|
| `field` | `FieldLike` | Field name or Field object. |
| `value` | `AnyExpression` | Value or expression. |

**Returns:** `Self`

```python
Pipeline().set_field("status", "processed")
```

---

### unset()

```python
def unset(self, *fields: FieldLike) -> Self
```

Add an `$unset` stage. Removes specified fields from documents.

| Parameter | Type | Description |
|---|---|---|
| `*fields` | `FieldLike` | Field names or Field objects to remove. |

**Returns:** `Self`

```python
Pipeline().unset("_id", "internal", "temp")
```

**Compiles to:**
```json
[{"$unset": ["_id", "internal", "temp"]}]
```

---

### unwind()

```python
def unwind(
    self,
    field: FieldLike,
    /,
    *,
    include_array_index: str | None = None,
    preserve_null_and_empty_arrays: bool | None = None,
) -> Self
```

Add an `$unwind` stage. Deconstructs an array field into one document per element.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `field` | `FieldLike` | _(required)_ | Array field to unwind (must be a path, e.g., `"$tags"`). |
| `include_array_index` | `str \| None` | `None` | Name of field to hold the array index. |
| `preserve_null_and_empty_arrays` | `bool \| None` | `None` | If `True`, output documents for null or empty arrays. |

**Returns:** `Self`

```python
Pipeline().unwind("$items", include_array_index="idx", preserve_null_and_empty_arrays=True)
```

**Compiles to:**
```json
[{"$unwind": {"path": "$items", "includeArrayIndex": "idx", "preserveNullAndEmptyArrays": true}}]
```

---

### bucket()

```python
def bucket(
    self,
    *output: Aliased | dict | list | None,
    by: AnyExpression,
    boundaries: list[T],
    default: str | None = None,
) -> Self
```

Add a `$bucket` stage. Categorizes documents into buckets based on specified boundaries.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `*output` | `dict`, `list[Aliased]`, spread `Aliased`, or `None` | _(optional)_ | Accumulator output definitions. |
| `by` | `AnyExpression` | _(required)_ | Expression to group by. |
| `boundaries` | `list[T]` | _(required)_ | Boundary values for buckets. |
| `default` | `str \| None` | `None` | Bucket name for documents outside boundaries. |

**Returns:** `Self`

```python
Pipeline().bucket(
    {"count": Sum(1)},
    by="$age",
    boundaries=[0, 18, 65, 100],
    default="other",
)
```

---

### bucket_auto()

```python
def bucket_auto(
    self,
    *output: Aliased | dict | list | None,
    by: AnyExpression,
    buckets: int,
    granularity: Granularity | None = None,
) -> Self
```

Add a `$bucketAuto` stage. Automatically distributes documents into a specified number of buckets.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `*output` | `dict`, `list[Aliased]`, spread `Aliased`, or `None` | _(optional)_ | Accumulator output definitions. |
| `by` | `AnyExpression` | _(required)_ | Expression to group by. |
| `buckets` | `int` | _(required)_ | Number of buckets. |
| `granularity` | `Granularity \| None` | `None` | Preferred number series: `"R5"`, `"R10"`, `"R20"`, `"R40"`, `"R80"`, `"1-2-5"`, `"E6"`, `"E12"`, `"E24"`, `"E48"`, `"E96"`, `"E192"`, `"POWERSOF2"`. |

**Returns:** `Self`

```python
Pipeline().bucket_auto(by="$price", buckets=5)
```

---

### lookup()

```python
def lookup(
    self,
    other: CollectionPipeline | DocumentsPipeline | type[Model],
    /,
    *,
    local_field: FieldLike | None = None,
    foreign_field: FieldLike | None = None,
    into: FieldLike,
) -> Self
```

Add a `$lookup` stage. Performs a left outer join to another collection.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `other` | `CollectionPipeline`, `DocumentsPipeline`, or `type[Model]` | _(required)_ | The foreign collection or pipeline. |
| `local_field` | `FieldLike \| None` | `None` | Local field for equality match. |
| `foreign_field` | `FieldLike \| None` | `None` | Foreign field for equality match. |
| `into` | `FieldLike` | _(required)_ | Name of the output array field. |

**Returns:** `Self`

```python
# Simple lookup with Model
Pipeline().lookup(Order, local_field="user_id", foreign_field="_id", into="orders")

# Lookup with sub-pipeline
sub = CollectionPipeline("orders").match({"status": "completed"})
Pipeline().lookup(sub, into="completed_orders")

# Lookup with in-memory documents
docs = Pipeline.documents([{"id": 1, "label": "Premium"}])
Pipeline().lookup(docs, local_field="tier_id", foreign_field="id", into="tier")
```

---

### graph_lookup()

```python
def graph_lookup(
    self,
    other: type[Model],
    /,
    start_with: FieldLike,
    local_field: FieldLike,
    foreign_field: FieldLike,
    into: FieldLike,
    max_depth: int | None = None,
    depth_field: FieldLike | None = None,
    restrict_search_with_match: MongoQuery | Predicate | None = None,
) -> Self
```

Add a `$graphLookup` stage. Performs a recursive search on a collection.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `other` | `type[Model]` | _(required)_ | Model class for the foreign collection. |
| `start_with` | `FieldLike` | _(required)_ | Expression for the starting value. |
| `local_field` | `FieldLike` | _(required)_ | Field from local documents for connection. |
| `foreign_field` | `FieldLike` | _(required)_ | Field from foreign documents for connection. |
| `into` | `FieldLike` | _(required)_ | Output array field name. |
| `max_depth` | `int \| None` | `None` | Maximum recursion depth. |
| `depth_field` | `FieldLike \| None` | `None` | Field to store recursion depth. |
| `restrict_search_with_match` | `MongoQuery \| Predicate \| None` | `None` | Additional filter on foreign documents. |

**Returns:** `Self`

```python
Pipeline().graph_lookup(
    Employee,
    start_with="$reports_to",
    local_field="reports_to",
    foreign_field="employee_id",
    into="reporting_chain",
    max_depth=5,
)
```

---

### facet()

```python
def facet(self, *facets: Aliased[Pipeline] | dict | list) -> Self
```

Add a `$facet` stage. Processes multiple pipelines within a single stage on the same input documents.

| Parameter | Type | Description |
|---|---|---|
| `*facets` | `dict[str, Pipeline]`, `list[Aliased[Pipeline]]`, or spread `Aliased[Pipeline]` | Facet definitions. |

**Returns:** `Self`

```python
# Dict form
Pipeline().facet({
    "count": Pipeline().count("total"),
    "items": Pipeline().sort({"age": -1}).take(10),
})

# Spread Aliased form
Pipeline().facet(
    Pipeline().count("total").alias("count"),
    Pipeline().sort({"age": -1}).take(10).alias("items"),
)
```

**Compiles to:**
```json
[{"$facet": {"count": [{"$count": "total"}], "items": [{"$sort": {"age": -1}}, {"$limit": 10}]}}]
```

---

### union_with()

```python
def union_with(self, other: CollectionPipeline | type[Model], /) -> Self
```

Add a `$unionWith` stage. Combines results from two collections.

| Parameter | Type | Description |
|---|---|---|
| `other` | `CollectionPipeline \| type[Model]` | Collection pipeline or Model class to union with. |

**Returns:** `Self`

```python
# Union with a Model class
Pipeline().union_with(ArchivedUser)

# Union with a CollectionPipeline
sub = CollectionPipeline("archived_users").match({"year": 2024})
Pipeline().union_with(sub)
```

---

### count()

```python
def count(self, output: FieldLike, /) -> Self
```

Add a `$count` stage. Returns the count of documents at this stage.

| Parameter | Type | Description |
|---|---|---|
| `output` | `FieldLike` | Name of the output field for the count. |

**Returns:** `Self`

```python
Pipeline().match({"status": "active"}).count("active_count")
```

**Compiles to:**
```json
[{"$match": {"status": "active"}}, {"$count": "active_count"}]
```

---

### sample()

```python
def sample(self, size: PositiveInteger | None, /) -> Self
```

Add a `$sample` stage. Randomly selects the specified number of documents.

| Parameter | Type | Description |
|---|---|---|
| `size` | `int \| None` | Number of documents to sample. `None` is a no-op. |

**Returns:** `Self`

```python
Pipeline().sample(5)
```

**Compiles to:**
```json
[{"$sample": {"size": 5}}]
```

---

### replace_with()

```python
def replace_with(self, expr: AnyExpression, /) -> Self
```

Add a `$replaceWith` stage. Replaces each document with the specified expression.

| Parameter | Type | Description |
|---|---|---|
| `expr` | `AnyExpression` | Expression or document to replace with. |

**Returns:** `Self`

```python
Pipeline().replace_with("$user")
Pipeline().replace_with({"name": "$fullName", "age": "$person_age"})
```

---

### set_window_fields()

```python
def set_window_fields(
    self,
    *output: Aliased[WindowOperator] | dict | list,
    sort_by: SortPayload | None = None,
    partition_by: AnyExpression | None = None,
) -> Self
```

Add a `$setWindowFields` stage. Performs window operations over document ranges.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `*output` | `dict`, `list[Aliased]`, or spread `Aliased` | _(required)_ | Window operator definitions. |
| `sort_by` | `SortPayload \| None` | `None` | Sort within partitions. |
| `partition_by` | `AnyExpression \| None` | `None` | Expression to partition documents. |

**Returns:** `Self`

---

### raw()

```python
def raw(self, *stages: Stage | Step) -> Self
```

Add raw MongoDB aggregation stage(s) to the pipeline.

| Parameter | Type | Description |
|---|---|---|
| `*stages` | `Stage \| Step` | Raw stage dicts or Step objects. |

**Returns:** `Self`

```python
Pipeline().raw({"$customStage": {"option": "value"}})
Pipeline().raw({"$stage1": {}}, {"$stage2": {}})
```

---

### pipe()

```python
def pipe(
    self,
    _0: Callable[[Self, *P.args, **P.kwargs], Self],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Self
```

Apply a user-defined function to the pipeline. The function receives the pipeline as its first argument.

| Parameter | Type | Description |
|---|---|---|
| `_0` | `Callable` | Function that takes a Pipeline and returns a Pipeline. |
| `*args` | `Any` | Positional arguments forwarded to the function. |
| `**kwargs` | `Any` | Keyword arguments forwarded to the function. |

**Returns:** `Self`

```python
def add_active_filter(pipeline: Pipeline) -> Pipeline:
    return pipeline.match(Field("status").eq("active"))

Pipeline().pipe(add_active_filter).sort({"name": 1})
```

---

### build()

```python
def build(self, *, context: Context | None = None) -> list[Stage]
```

Compile the pipeline into a list of MongoDB aggregation stage dicts.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `context` | `Context \| None` | `None` | Optional compilation context dict. |

**Returns:** `list[Stage]` -- A list of MongoDB aggregation stage dicts ready to pass to PyMongo.

```python
pipeline = Pipeline().match({"status": "active"}).sort({"age": -1}).take(10)
stages = pipeline.build()
# [{"$match": {"status": "active"}}, {"$sort": {"age": -1}}, {"$limit": 10}]
```

---

### alias()

```python
def alias(self, ref: str) -> Aliased[Self]
```

Wrap the pipeline in an `Aliased` container with a name. Used primarily with `facet()`.

| Parameter | Type | Description |
|---|---|---|
| `ref` | `str` | The alias name. |

**Returns:** `Aliased[Pipeline]`

```python
Pipeline().count("total").alias("count")
# Used in: Pipeline().facet(Pipeline().count("total").alias("count"))
```

---

### documents() (class method)

```python
@classmethod
def documents(cls, *documents: Document | list[Document]) -> DocumentsPipeline
```

Create a `DocumentsPipeline` with in-memory documents. The resulting pipeline starts with a `$documents` stage.

| Parameter | Type | Description |
|---|---|---|
| `*documents` | `Document` or `list[Document]` | Documents as spread dicts or a single list. |

**Returns:** `DocumentsPipeline`

```python
# Spread form
docs = Pipeline.documents(
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
)

# List form
docs = Pipeline.documents([
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
])

# Use with lookup
Pipeline().lookup(docs, local_field="ref_id", foreign_field="id", into="refs")
```

---

### add_step()

```python
def add_step(self, step: Step, /) -> Self
```

Low-level method to add a `Step` object to the pipeline. Usually called internally by the higher-level methods.

| Parameter | Type | Description |
|---|---|---|
| `step` | `Step` | A Step object. |

**Returns:** `Self`

---

## CollectionPipeline

```python
@dataclass
class CollectionPipeline(Pipeline)
```

A `Pipeline` associated with a specific MongoDB collection name. Used with `lookup()` and `union_with()` to reference a foreign collection with a sub-pipeline.

### Constructor

```python
CollectionPipeline(collection: str, *, steps: list[Step] = [])
```

| Parameter | Type | Description |
|---|---|---|
| `collection` | `str` | The MongoDB collection name. |

### Example

```python
sub = CollectionPipeline("orders").match({"status": "completed"}).sort({"date": -1})
Pipeline().lookup(sub, into="recent_orders")
```

---

## DocumentsPipeline

```python
@dataclass
class DocumentsPipeline(Pipeline)
```

A `Pipeline` that starts with a `$documents` stage containing in-memory documents. Created via `Pipeline.documents()`.

### Constructor

```python
DocumentsPipeline(documents: list[Document], *, steps: list[Step] = [])
```

| Parameter | Type | Description |
|---|---|---|
| `documents` | `list[Document]` | The in-memory documents. |

### build()

Overrides `Pipeline.build()` to prepend a `{"$documents": [...]}` stage before any other steps.

```python
docs = Pipeline.documents([{"id": 1}, {"id": 2}])
stages = docs.build()
# [{"$documents": [{"id": 1}, {"id": 2}]}]
```
