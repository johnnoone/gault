# Manager

The Manager classes provide the main interface for querying and persisting MongoDB documents. `AsyncManager` is for async/await code; `Manager` is the synchronous equivalent. Both share identical method signatures and semantics.

## AsyncManager

```python
class AsyncManager
```

Asynchronous manager for MongoDB operations. Uses PyMongo's async driver.

### Constructor

```python
AsyncManager(
    database: AsyncDatabase[Document],
    *,
    persistence: Persistence | None = None,
    state_tracker: StateTracker | None = None,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `database` | `AsyncDatabase[Document]` | _(required)_ | A PyMongo async database instance. |
| `persistence` | `Persistence \| None` | `None` | Tracks which instances have been persisted. Created lazily if not provided. |
| `state_tracker` | `StateTracker \| None` | `None` | Tracks dirty fields for atomic saves. Created lazily if not provided. |

### Properties

| Property | Type | Description |
|---|---|---|
| `persistence` | `Persistence` | The persistence tracker (created lazily on first access). |
| `state_tracker` | `StateTracker` | The state tracker (created lazily on first access). |

---

### get()

```python
async def get(self, model: type[M], filter: Filter = None) -> M
```

Retrieve a single document matching the filter. Raises `NotFound` if no document matches.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `type[M]` | _(required)_ | The Model or Schema class to query. |
| `filter` | `Filter` | `None` | Query filter (see [Filter type](#filter-type)). |

**Returns:** `M` -- An instance of the model class.

**Raises:**

| Exception | Condition |
|---|---|
| `NotFound` | No document matches the filter. |

```python
user = await manager.get(User, User.id == "abc123")
```

---

### find()

```python
async def find(self, model: type[M], filter: Filter = None) -> M | None
```

Retrieve a single document matching the filter, or `None` if not found.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `type[M]` | _(required)_ | The Model or Schema class to query. |
| `filter` | `Filter` | `None` | Query filter. |

**Returns:** `M | None`

```python
user = await manager.find(User, User.email.eq("alice@example.com"))
if user:
    print(user.name)
```

---

### select()

```python
async def select(
    self,
    model: type[M],
    filter: Filter = None,
    *,
    skip: int | None = None,
    take: int | None = None,
) -> AsyncIterator[M]
```

Iterate over documents matching the filter. Returns an async iterator.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `type[M]` | _(required)_ | The Model or Schema class to query. |
| `filter` | `Filter` | `None` | Query filter. |
| `skip` | `int \| None` | `None` | Number of documents to skip. |
| `take` | `int \| None` | `None` | Maximum number of documents to return. |

**Returns:** `AsyncIterator[M]`

```python
async for user in manager.select(User, User.age.gte(18), take=100):
    print(user.name)
```

---

### insert()

```python
async def insert(self, instance: S) -> S
```

Insert a new document into the collection. The instance must be a `Schema` subclass.

| Parameter | Type | Description |
|---|---|---|
| `instance` | `S` (bound to `Schema`) | The schema instance to insert. |

**Returns:** `S` -- The same instance, now marked as persisted.

**Raises:**

| Exception | Condition |
|---|---|
| `Forbidden` | The instance is not a `Schema` subclass. |

```python
user = User(id="abc123", name="Alice", email="alice@example.com")
await manager.insert(user)
```

---

### save()

```python
async def save(
    self,
    instance: S,
    *,
    refresh: bool = False,
    atomic: bool = False,
) -> S
```

Upsert a document. Uses `find_one_and_update` with `upsert=True`. The instance must be a `Schema` subclass with at least one field marked as `pk=True`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `instance` | `S` (bound to `Schema`) | _(required)_ | The schema instance to save. |
| `refresh` | `bool` | `False` | If `True`, update the instance's attributes with the values returned from MongoDB after the save. |
| `atomic` | `bool` | `False` | If `True` and the instance is already persisted, only send dirty (changed) fields in `$set`; unchanged fields go into `$setOnInsert`. |

**Returns:** `S` -- The instance, marked as persisted with a fresh state snapshot.

**Raises:**

| Exception | Condition |
|---|---|
| `Forbidden` | The instance is not a `Schema` subclass. |
| `Unprocessable` | The model has no field marked as `pk=True`. |

```python
user.name = "Alice Updated"
await manager.save(user, refresh=True, atomic=True)
```

---

### refresh()

```python
async def refresh(self, instance: M) -> M
```

Reload an instance's data from MongoDB. The model must have at least one `pk` field so a filter can be constructed.

| Parameter | Type | Description |
|---|---|---|
| `instance` | `M` | The model instance to refresh. |

**Returns:** `M` -- The same instance with updated attribute values.

**Raises:**

| Exception | Condition |
|---|---|
| `Unprocessable` | The model has no `pk` field. |
| `NotFound` | The document no longer exists in the database. |

```python
await manager.refresh(user)
print(user.name)  # reflects the current database state
```

---

### paginate()

```python
async def paginate(
    self,
    model: type[M],
    filter: Filter = None,
    *,
    page: int = 1,
    per_page: int = 10,
    sort_by: SortPayload | None = None,
) -> Page[M]
```

Retrieve a paginated result set. Uses `$facet` internally to get total count and page items in a single aggregation.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `type[M]` | _(required)_ | The Model or Schema class to query. |
| `filter` | `Filter` | `None` | Query filter. |
| `page` | `int` | `1` | Page number (1-based). |
| `per_page` | `int` | `10` | Items per page. |
| `sort_by` | `SortPayload \| None` | `None` | Sort specification (see [Sorting](#sorting)). |

**Returns:** `Page[M]`

```python
page = await manager.paginate(
    User,
    User.age.gte(18),
    page=2,
    per_page=25,
    sort_by=User.name.asc(),
)
print(page.total)  # total matching documents
for user in page:
    print(user.name)
```

---

## Manager

```python
class Manager(Generic[M, S])
```

Synchronous equivalent of `AsyncManager`. All methods have identical signatures and semantics, but are synchronous. `select()` returns `Iterator[M]` instead of `AsyncIterator[M]`.

### Constructor

```python
Manager(
    database: Database[Document],
    *,
    persistence: Persistence | None = None,
    state_tracker: StateTracker | None = None,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `database` | `Database[Document]` | _(required)_ | A PyMongo synchronous database instance. |
| `persistence` | `Persistence \| None` | `None` | Tracks which instances have been persisted. |
| `state_tracker` | `StateTracker \| None` | `None` | Tracks dirty fields for atomic saves. |

### Methods

All methods are identical to `AsyncManager` but synchronous:

| Method | Signature | Returns |
|---|---|---|
| `get()` | `get(model, filter=None)` | `M` |
| `find()` | `find(model, filter=None)` | `M \| None` |
| `select()` | `select(model, filter=None, *, skip=None, take=None)` | `Iterator[M]` |
| `insert()` | `insert(instance)` | `S` |
| `save()` | `save(instance, *, refresh=False, atomic=False)` | `S` |
| `refresh()` | `refresh(instance)` | `M` |
| `paginate()` | `paginate(model, filter=None, *, page=1, per_page=10, sort_by=None)` | `Page[M]` |

---

## Filter type

The `Filter` type alias accepted by all query methods:

```python
Filter = Predicate | Pipeline | MongoQuery | list[Stage] | None
```

| Type | Description |
|---|---|
| `None` | No filter -- match all documents. |
| `Predicate` | A gault predicate object (e.g., `Field("age").gte(18)`). |
| `Pipeline` | A full aggregation pipeline. |
| `MongoQuery` | A raw MongoDB query dict (e.g., `{"age": {"$gte": 18}}`). |
| `list[Stage]` | A list of raw aggregation stage dicts. |

All filter types are normalized into a `Pipeline` internally.

---

## Sorting

The `SortPayload` type accepted by `paginate()` and `Pipeline.sort()`:

```python
SortPayload = SortToken | list[SortToken] | Mapping[FieldLike, Direction | None]
SortToken = FieldLike | tuple[FieldLike, Direction | None]
Direction = 1 | -1 | {"$meta": str}
```

Examples:

```python
# Single field ascending (string)
sort_by="name"

# Using AttributeSpec
sort_by=User.name.asc()

# Multiple tokens
sort_by=[User.age.desc(), User.name.asc()]

# Dict
sort_by={"age": -1, "name": 1}
```

---

## Persistence

```python
class Persistence
```

Tracks which model instances have been persisted to the database. Uses a `WeakSet` so instances can be garbage-collected normally.

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `is_persisted()` | `is_persisted(instance: Model)` | `bool` | Check if the instance has been persisted. |
| `mark_persisted()` | `mark_persisted(instance: Model)` | `None` | Mark the instance as persisted. |
| `forget()` | `forget(instance: Model)` | `None` | Remove the instance from the persisted set. |

### Example

```python
persistence = Persistence()
user = User(id="1", name="Alice")

assert persistence.is_persisted(user) is False

persistence.mark_persisted(user)
assert persistence.is_persisted(user) is True

persistence.forget(user)
assert persistence.is_persisted(user) is False
```

---

## StateTracker

```python
class StateTracker
```

Tracks the state of model instances to detect dirty (changed) fields. Uses `WeakKeyDictionary` so instances can be garbage-collected normally. State snapshots are deep copies.

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `snapshot()` | `snapshot(instance: Model)` | `None` | Save a deep copy of the instance's current state. |
| `reset()` | `reset(instance: Model)` | `None` | Restore the instance to its last snapshot. |
| `get_dirty_fields()` | `get_dirty_fields(instance: Model)` | `set[str]` | Return field names that have changed since the last snapshot. |

### Example

```python
tracker = StateTracker()
user = User(id="1", name="Alice")

tracker.snapshot(user)
user.name = "Bob"

dirty = tracker.get_dirty_fields(user)
assert dirty == {"name"}

tracker.reset(user)
assert user.name == "Alice"
```
