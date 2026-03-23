# Use Aggregation Pipelines

This guide covers how to compose MongoDB aggregation pipelines using Gault's `Pipeline` class.

## Setup

```python
from gault import Pipeline, Schema, configure, AsyncManager
from gault.predicates import Field
from gault.accumulators import Sum, Avg, Count
from gault.pipelines import CollectionPipeline

class Order(Schema, collection="orders"):
    id: Field[int] = configure(pk=True)
    customer_id: Field[int]
    amount: Field[float]
    status: Field[str]
    tags: Field[list]

class Customer(Schema, collection="customers"):
    id: Field[int] = configure(pk=True)
    name: Field[str]
    referred_by: Field[int]
```

## Pipeline basics

`Pipeline` is immutable. Every method returns a new pipeline instance:

```python
p1 = Pipeline().match(Order.status == "active")
p2 = p1.sort(Order.amount.desc())   # p1 is unchanged
p3 = p2.take(10)                     # p2 is unchanged
```

Convert to raw MongoDB stages with `.build()`:

```python
stages = p3.build()
# [
#     {"$match": {"status": {"$eq": "active"}}},
#     {"$sort": {"amount": -1}},
#     {"$limit": 10}
# ]
```

Pass pipelines directly to manager methods:

```python
async for order in manager.select(Order, filter=p3):
    print(order.amount)
```

## Faceted aggregation with `facet()`

Run multiple sub-pipelines on the same input in a single pass:

```python
pipeline = Pipeline().match(Order.status == "active").facet(
    Pipeline().count("total").alias("count"),
    Pipeline().group({"avg_amount": Avg("$amount")}, by=None).alias("stats"),
    Pipeline().group({"total": Sum("$amount")}, by="$customer_id").alias("by_customer"),
)
```

You can also pass a dict:

```python
pipeline = Pipeline().facet({
    "count": Pipeline().count("total"),
    "stats": Pipeline().group({"avg_amount": Avg("$amount")}, by=None),
})
```

## Joining collections with `lookup()`

### Simple lookup by field equality

```python
pipeline = Pipeline().lookup(
    Customer,
    local_field="customer_id",
    foreign_field="_id",
    into="customer_info",
)
```

### Lookup with a sub-pipeline

Use `CollectionPipeline` to apply filtering or transformation on the joined collection:

```python
active_orders = CollectionPipeline("orders").match(Order.status == "completed")

pipeline = Pipeline().lookup(active_orders, into="completed_orders")
```

### Lookup with in-memory documents

```python
docs = Pipeline.documents(
    {"code": "A", "label": "Category A"},
    {"code": "B", "label": "Category B"},
)
pipeline = Pipeline().lookup(docs, local_field="category", foreign_field="code", into="category_info")
```

## Recursive search with `graph_lookup()`

Traverse hierarchical or graph-structured data:

```python
pipeline = Pipeline().graph_lookup(
    Customer,
    start_with="$referred_by",
    local_field="referred_by",
    foreign_field="_id",
    into="referral_chain",
    max_depth=5,
)
```

Additional options:

```python
pipeline = Pipeline().graph_lookup(
    Customer,
    start_with="$referred_by",
    local_field="referred_by",
    foreign_field="_id",
    into="referral_chain",
    max_depth=3,
    depth_field="depth",
    restrict_search_with_match=Customer.status == "active",
)
```

## Bucketing with `bucket()` and `bucket_auto()`

### Manual boundaries

```python
pipeline = Pipeline().bucket(
    {"count": Sum(1), "total_amount": Sum("$amount")},
    by="$amount",
    boundaries=[0, 100, 500, 1000, 5000],
    default="other",
)
```

### Automatic buckets

```python
pipeline = Pipeline().bucket_auto(
    {"count": Sum(1), "avg_amount": Avg("$amount")},
    by="$amount",
    buckets=5,
)
```

An optional `granularity` parameter controls the preferred number series for boundaries (e.g., `"R5"`, `"POWERSOF2"`).

## Unwinding arrays with `unwind()`

Deconstruct an array field into one document per element:

```python
pipeline = Pipeline().unwind("$tags")
```

Preserve documents with empty or missing arrays:

```python
pipeline = Pipeline().unwind(
    "$tags",
    preserve_null_and_empty_arrays=True,
)
```

Track the original array index:

```python
pipeline = Pipeline().unwind(
    "$tags",
    include_array_index="tag_index",
)
```

## `CollectionPipeline`

`CollectionPipeline` binds a pipeline to a specific collection name. It is used as the `other` argument in `lookup()` and `union_with()`:

```python
from gault.pipelines import CollectionPipeline

archived = CollectionPipeline("orders").match({"status": "archived"})

# Use in lookup
pipeline = Pipeline().lookup(archived, into="archived_orders")

# Use in union
pipeline = Pipeline().union_with(archived)
```

## Custom transforms with `pipe()`

`pipe()` passes the current pipeline as the first argument to a callable, enabling reusable pipeline fragments:

```python
def paginate(p: Pipeline, page: int, size: int) -> Pipeline:
    return p.skip((page - 1) * size).take(size)

def active_only(p: Pipeline) -> Pipeline:
    return p.match(Order.status == "active")

pipeline = (
    Pipeline()
    .pipe(active_only)
    .sort(Order.amount.desc())
    .pipe(paginate, 3, 20)
)
```

This keeps pipeline construction readable and composable without inheritance.

## Other useful stages

### Grouping

```python
Pipeline().group(
    {"total": Sum("$amount"), "count": Count()},
    by="$status",
)
```

### Adding/removing fields

```python
Pipeline().set({"full_total": {"$multiply": ["$amount", "$quantity"]}})
Pipeline().set_field("processed", True)
Pipeline().unset("_id", "internal_field")
```

### Counting

```python
Pipeline().match(Order.status == "active").count("active_count")
```

### Random sampling

```python
Pipeline().sample(10)
```

### Replace document root

```python
Pipeline().replace_with("$nested_doc")
```

### Raw stages

For any stage not covered by the fluent API:

```python
Pipeline().raw({"$densify": {"field": "timestamp", "range": {"step": 1, "unit": "hour"}}})
```

## In-memory testing with `Pipeline.documents()`

Create a pipeline seeded with in-memory documents for testing without a database:

```python
pipeline = Pipeline.documents(
    {"id": 1, "amount": 100, "status": "active"},
    {"id": 2, "amount": 200, "status": "completed"},
    {"id": 3, "amount": 50, "status": "active"},
).match(Field("status").eq("active"))

stages = pipeline.build()
# [{"$documents": [...]}, {"$match": {"status": {"$eq": "active"}}}]
```

When passed to `manager.select()`, documents-based pipelines are executed against `database.aggregate()` rather than a specific collection.
