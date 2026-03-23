# Schema vs Model

Gault provides two base classes for defining the shape of your data: `Schema` and `Model`. At first glance they look almost identical -- both are decorated as dataclasses, both support the same `configure()` helper for field metadata, and both participate in the same pipeline and mapping machinery. So why have two?

The answer comes down to a single question: **does this class represent a MongoDB collection?**

## The two roles of a data shape

In a typical MongoDB application, you work with data in two very different contexts:

1. **Persistent documents** that live in a specific collection. These are the canonical source of truth. You insert them, update them, and query them by collection name.

2. **Transient shapes** that exist only in memory -- the result of an aggregation pipeline, a projection that cherry-picks fields from several collections, a view model shaped for a particular API response. These never get written back to any collection.

Gault makes this distinction explicit at the type level.

### Schema: the persistent side

A `Schema` subclass *must* declare a collection name:

```python
class User(Schema, collection="users"):
    id: ObjectId = configure(pk=True, db_alias="_id")
    name: str
    email: str
```

That `collection="users"` argument does two things:

1. It registers the class in the global `COLLECTIONS` mapping so that the manager knows which MongoDB collection to target for queries, inserts, and saves.
2. It registers the class in the global `SCHEMAS` mapping so that the collection name can be resolved back to its authoritative schema class.

Only `Schema` instances can be passed to `manager.insert()` or `manager.save()`. Attempting to persist a plain `Model` raises a `Forbidden` error. This is a deliberate guard rail: if a class was never associated with a collection, writing it to the database would be meaningless.

### Model: the non-persistent side

A `Model` subclass *may* declare a collection (for read-only querying), but it is not required to:

```python
class UserSummary(Model):
    name: str
    email: str
```

Models are ideal for:

- **Projections** -- when you only need a subset of fields from a collection.
- **Aggregation results** -- when a `$group` or `$bucket` stage produces a shape that does not correspond to any stored document.
- **View models** -- when you want a typed object to hand off to a serializer or template, without implying that it can be saved.

A `Model` can still be used with `manager.select()` (the manager will use the pipeline's `$project` stage to reshape documents into the model's fields), but it cannot be inserted or saved.

## How the collection registry works

Gault maintains two module-level dictionaries in `models.py`:

```
SCHEMAS: WeakValueDictionary[str, type[Schema]]
COLLECTIONS: WeakKeyDictionary[type[Model], str]
```

```
                  +-----------+          +------------+
                  | SCHEMAS   |          | COLLECTIONS|
                  +-----------+          +------------+
                  |           |          |            |
  "users"  ----> | User      |          | User ------+--> "users"
  "orders" ----> | Order     |          | Order -----+--> "orders"
                  |           |          |            |
                  +-----------+          +------------+
```

`COLLECTIONS` maps a model *class* to its collection name. Both `Schema` and `Model` subclasses end up here when they declare `collection=...`. This is the lookup used by `get_collection()` every time the manager needs to know where to send a query.

`SCHEMAS` maps a collection *name* back to its `Schema` class. Only `Schema` subclasses are registered here. This reverse lookup is useful when you have a collection name (perhaps from a `$lookup` or `$unionWith` stage) and need to resolve the authoritative class for that collection.

### Why WeakReferences?

Both dictionaries use weak references (`WeakValueDictionary` and `WeakKeyDictionary`). This is a pragmatic choice for long-running applications and test suites:

- If a model class is redefined or goes out of scope (common in tests that dynamically create classes), the registry entries are automatically cleaned up by the garbage collector.
- There is no risk of the registry preventing class objects from being collected, which would otherwise constitute a memory leak.

In practice, model classes defined at module level are never garbage-collected, so the weak references behave identically to strong references during normal application lifetime. The benefit surfaces in edge cases -- test isolation, hot-reloading, and dynamic class creation.

## How configure() bridges dataclasses and Gault

Gault models are standard Python dataclasses. The `configure()` function is a thin wrapper around `dataclasses.field()` that channels Gault-specific metadata (like `pk` and `db_alias`) through the dataclass `metadata` dict:

```python
class User(Schema, collection="users"):
    id: ObjectId = configure(pk=True, db_alias="_id")
    name: str
```

Under the hood, `configure(pk=True, db_alias="_id")` returns:

```python
field(default=MISSING, metadata={"pk": True, "db_alias": "_id"})
```

When `__init_subclass__` fires, Gault iterates over the dataclass fields and reads this metadata to construct `Attribute` descriptors. The metadata is also read later by the `Mapper` to build the correspondence between Python attribute names and MongoDB field names.

This design keeps Gault firmly in the dataclass ecosystem. Your models remain compatible with `dataclasses.asdict()`, type checkers, and any tooling that understands standard dataclasses -- because they *are* standard dataclasses, augmented with metadata.

## The Attribute descriptor

When you access a field on a model *class* (not an instance), Gault returns an `AttributeSpec` rather than a raw value:

```python
User.name   # --> AttributeSpec(User, 'name')
```

This is powered by the `Attribute` descriptor's `__get__` method, which checks whether `instance is None`. On a class access, it returns an `AttributeSpec` that knows how to compile itself into MongoDB field references, expressions, sort tokens, and query predicates. On an instance access, it returns the plain value from the instance's `__dict__`.

This dual behavior is what makes Gault's query API feel natural:

```python
# Class access: builds a predicate
pipeline.match(User.name == "Alice")

# Instance access: returns the value
user = User(name="Alice", ...)
print(user.name)  # "Alice"
```

## When to use which

| Concern | Schema | Model |
|---|---|---|
| Tied to a collection | Always | Optionally |
| Can be inserted/saved | Yes | No |
| Can be queried | Yes | Yes (if collection is declared) |
| Registered in SCHEMAS | Yes | No |
| Use case | Canonical documents | Projections, aggregation results, view models |

The rule of thumb: if you would ever write `manager.save(instance)`, it should be a `Schema`. If you only ever *read* data into it, a `Model` is the lighter-weight and more intention-revealing choice.
