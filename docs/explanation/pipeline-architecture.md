# Pipeline Architecture

MongoDB's aggregation framework is powerful, but its raw JSON representation is verbose, error-prone, and hard to compose. Gault's `Pipeline` class provides a Pythonic builder that compiles down to native aggregation stages while staying composable, immutable, and type-safe.

This article explains the design decisions behind the pipeline system.

## Immutability: every method returns a new Pipeline

The most important architectural decision is that **Pipeline is immutable**. Every method -- `match()`, `sort()`, `project()`, `group()`, and so on -- returns a *new* `Pipeline` instance with the additional step appended. The original pipeline is never modified.

```python
base = Pipeline().match(User.active == True)
branch_a = base.sort(User.name.asc()).take(10)
branch_b = base.group({"count": Count()}, by=User.role.expr())
```

Here, `base`, `branch_a`, and `branch_b` are three independent pipelines. Appending steps to `branch_a` does not affect `base` or `branch_b`. This is possible because `Pipeline` is a dataclass and `add_step()` uses `dataclasses.replace()` to produce a shallow copy with a new steps list:

```python
def add_step(self, step: Step, /) -> Self:
    return replace(self, steps=[*self.steps, step])
```

This immutability has several practical benefits:

- **Safe sharing.** You can define a base pipeline (say, a common set of filters) and derive specialized pipelines from it without worrying about mutation.
- **Thread safety.** Immutable objects can be shared across threads without synchronization.
- **Debuggability.** Each pipeline is a complete, self-contained description of the aggregation it represents. There is no hidden mutable state to inspect.

## Steps: the intermediate representation

A `Pipeline` does not hold MongoDB stages directly. Instead, it holds a list of `Step` objects -- dataclasses that capture the *intent* of each operation in a structured form:

```
Pipeline
  steps: [
    MatchStep(query=...),
    SortStep(spec=...),
    ProjectStep(projection=...),
  ]
```

Each `Step` subclass knows how to `compile()` itself into one or more MongoDB stages:

```python
class Step(ABC):
    @abstractmethod
    def compile(self, context: Context) -> Iterator[Stage]: ...
```

The return type is `Iterator[Stage]` rather than a single `Stage` because some logical operations may produce multiple MongoDB stages, and the abstraction needs to accommodate that.

Here is a sampling of the Step subclasses and what they compile to:

| Step class | MongoDB stage(s) |
|---|---|
| `MatchStep` | `{"$match": ...}` |
| `SortStep` | `{"$sort": ...}` |
| `ProjectStep` | `{"$project": ...}` |
| `GroupStep` | `{"$group": ...}` |
| `LookupStep` | `{"$lookup": ...}` |
| `FacetStep` | `{"$facet": ...}` |
| `UnwindStep` | `{"$unwind": ...}` |
| `SetStep` | `{"$set": ...}` |
| `UnsetStep` | `{"$unset": ...}` |
| `CountStep` | `{"$count": ...}` |
| `BucketStep` | `{"$bucket": ...}` |
| `RawStep` | Any arbitrary stage dict |

The `RawStep` is the escape hatch. When Gault does not provide a dedicated method for a particular MongoDB stage, you can pass a raw dict through `Pipeline.raw({"$customStage": {...}})`. This ensures the pipeline abstraction never blocks you from using MongoDB's full feature set.

### Why not store stages directly?

Storing structured Step objects rather than raw dicts has a key advantage: **deferred compilation**. The Step captures high-level intent using Gault's own types (model fields, predicates, accumulators), and the translation to MongoDB's wire format happens only at `build()` time. This separation means:

- Steps can reference model attributes symbolically. The actual MongoDB field name (which may differ from the Python attribute name via `db_alias`) is resolved during compilation.
- The compiler can apply optimizations or transformations across the full list of steps if needed in the future.
- Steps are easier to inspect and test than opaque dicts.

## The build() method: compiling steps into stages

`build()` walks the list of steps and concatenates their compiled output:

```python
def build(self, *, context: Context | None = None) -> list[Stage]:
    context = context or {}
    stages: list[Stage] = []
    for step in self.steps:
        stages += step.compile(context=context)
    return stages
```

The `context` parameter is a dictionary that can carry ambient information through the compilation process. Currently it is mostly used as a forward-looking extension point, but the compiler functions accept it uniformly.

The output of `build()` is a plain `list[dict]` -- exactly what PyMongo's `aggregate()` method expects. At this point, all Gault abstractions have been erased. What remains is pure MongoDB.

## The compiler system

Each Step's `compile()` method delegates to a set of compiler functions defined in `compilers.py`. These functions handle the translation from Gault's type-rich representations to MongoDB's string-based conventions:

### compile_field

Translates a field reference to a MongoDB field name string (no `$` prefix). Accepts either a plain string or an object implementing `AsRef` (like `AttributeSpec`):

```
User.name  -->  compile_field(...)  -->  "name"
User.id    -->  compile_field(...)  -->  "_id"   (via db_alias)
"status"   -->  compile_field(...)  -->  "status"
```

If you accidentally pass a string starting with `$`, the compiler raises a `CompilationError` -- it looks like you meant a *path* (expression reference), not a field name.

### compile_expression

Translates a value into a MongoDB expression. For objects implementing `ExpressionOperator`, it calls `compile_expression()` on them. For primitive types (strings, numbers, booleans, ObjectId, etc.), it returns the value as-is:

```
User.name       -->  compile_expression(...)  -->  "$name"
"$price"        -->  compile_expression(...)  -->  "$price"
42              -->  compile_expression(...)  -->  42
{"$add": [...]} -->  compile_expression(...)  -->  {"$add": [...]}
```

### compile_path

Similar to `compile_expression`, but specifically for field paths that *must* start with `$`. This is used in contexts like `$unwind` where MongoDB expects a path string:

```
User.tags  -->  compile_path(...)  -->  "$tags"
"$items"   -->  compile_path(...)  -->  "$items"
"items"    -->  compile_path(...)  -->  CompilationError!
```

### compile_query

Translates a predicate or raw dict into a MongoDB query document. For objects implementing `QueryPredicate`, it calls `compile_query()`. For objects implementing only `ExpressionOperator`, it wraps the result in `{"$expr": ...}`. For raw dicts, it passes them through:

```
User.age > 18        -->  compile_query(...)  -->  {"age": {"$gt": 18}}
{"status": "active"} -->  compile_query(...)  -->  {"status": "active"}
```

The relationship between these compilers can be visualized as:

```
                    +-----------------+
                    |  Step.compile() |
                    +-----------------+
                           |
              +------------+------------+
              |            |            |
              v            v            v
       compile_query  compile_field  compile_expression
              |            |            |
              v            v            v
     QueryPredicate     AsRef     ExpressionOperator
     (interface)      (interface)    (interface)
```

Each compiler function uses Python's structural pattern matching (`match`/`case`) to dispatch on the type of its input. This makes the compilation rules explicit and easy to extend.

## Flexible API with _normalize_aliased_args

Many pipeline methods accept arguments in multiple forms. For example, `group()` can be called with a dict, a list of `Aliased` objects, or spread `Aliased` arguments:

```python
# Dict form
Pipeline().group({"total": Sum("$amount")}, by="$category")

# List form
Pipeline().group([Sum("$amount").alias("total")], by="$category")

# Spread form
Pipeline().group(Sum("$amount").alias("total"), by="$category")
```

All three produce the same pipeline. The `_normalize_aliased_args` function handles this normalization:

```python
def _normalize_aliased_args(args: tuple[Any, ...]) -> list[Any] | None:
    if len(args) == 1:
        arg = args[0]
        if arg is None:
            return None
        if isinstance(arg, Mapping):
            return [Aliased(key, val) for key, val in arg.items()]
        if isinstance(arg, list):
            return arg
        return [arg]
    if args:
        return list(args)
    return None
```

The logic is straightforward:

- A single `None` argument means "no accumulators/fields specified."
- A single `Mapping` (dict) is unpacked into a list of `Aliased` pairs.
- A single `list` is used as-is.
- A single non-collection argument is wrapped in a list.
- Multiple arguments are collected into a list.

This pattern repeats across `group()`, `bucket()`, `set()`, `project()`, `facet()`, and `set_window_fields()`. It gives the API a flexible, Pythonic feel without sacrificing type safety -- each variant has its own `@overload` signature for type checkers to validate.

## CollectionPipeline and DocumentsPipeline

The base `Pipeline` is collection-agnostic. It represents a sequence of aggregation steps without knowing *where* they will run. Two subclasses add that context:

### CollectionPipeline

A `CollectionPipeline` pairs a pipeline with a specific collection name. It is used in contexts like `$lookup` and `$unionWith` where you need to reference a foreign collection:

```python
sub = CollectionPipeline("orders").match({"status": "completed"})
Pipeline().lookup(sub, into="recent_orders")
```

When `LookupStep` compiles, it reads `sub.collection` for the `from` field and calls `sub.build()` for the nested pipeline.

### DocumentsPipeline

A `DocumentsPipeline` holds a list of in-memory documents and prepends a `{"$documents": [...]}` stage when built. This maps to MongoDB's `$documents` stage, which injects literal documents into the aggregation pipeline:

```python
docs = Pipeline.documents({"id": 1, "label": "test"})
Pipeline().lookup(docs, local_field="ref", foreign_field="id", into="refs")
```

The manager has special handling for pipelines whose first stage is `$documents` -- these must be run via `database.aggregate()` rather than `collection.aggregate()`, because the documents are not sourced from any collection.

## How the Mapper bridges documents to instances

The pipeline produces MongoDB documents (plain dicts). The `Mapper` class converts these into typed model instances:

```
MongoDB document                  Mapper                    Model instance
{"_id": ObjectId(...),   --->   map(document)   --->   User(id=ObjectId(...),
 "name": "Alice",                                       name="Alice",
 "email": "a@b.com"}                                    email="a@b.com")
```

The mapper is constructed lazily (via `get_mapper()`) and cached in a `WeakKeyDictionary` keyed by the model class. It inspects the dataclass fields and their metadata to build a correspondence list between Python attribute names and MongoDB field names:

```
field_mapping = [
    Corres(model_field="id",    db_field="_id",   pk=True),
    Corres(model_field="name",  db_field="name",  pk=False),
    Corres(model_field="email", db_field="email", pk=False),
]
```

This correspondence is used in several directions:

- **map()** -- document to instance. Reads `db_field` keys from the document and passes them as `model_field` keyword arguments to the model constructor.
- **to_document()** -- instance to document. Reads `model_field` attributes from the instance and writes them under `db_field` keys.
- **to_filter()** -- instance to PK filter. Extracts only the PK fields, producing a filter suitable for `find_one`.
- **iter_document()** -- yields all field tuples for the save logic, including the `pk` flag that the atomic save flow uses to partition fields into filter, `$set`, and `$setOnInsert` buckets.

The mapper also exposes a `db_fields` set, which the `ProjectStep` uses to build the `$project` stage when projecting into a model class -- it includes exactly the fields the model knows about and excludes `_id` by default.

## Putting it all together

When you write:

```python
users = manager.select(User, Pipeline().match(User.active == True).sort(User.name.asc()))
```

The following sequence occurs:

1. `Pipeline().match(...)` creates a new Pipeline with a `MatchStep`.
2. `.sort(...)` creates another new Pipeline with the MatchStep plus a `SortStep`.
3. The manager appends a `ProjectStep(User)` to ensure only User's fields are returned.
4. `build()` compiles each Step in order, producing a list of MongoDB stages.
5. The stages are passed to PyMongo's `collection.aggregate()`.
6. Each returned document is run through `Mapper.map()` to produce a `User` instance.
7. The instance is marked as persisted and a state snapshot is taken.

The pipeline's immutability means steps 1-2 can happen anywhere in your code -- in a repository method, a utility function, a middleware -- and the resulting pipeline can be safely passed around, extended, or branched without side effects. The compilation in step 4 is the only point where Gault's abstractions meet MongoDB's concrete format, keeping the two worlds cleanly separated.
