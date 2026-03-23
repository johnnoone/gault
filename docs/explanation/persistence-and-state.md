# Persistence & State Tracking

When you load a document from MongoDB and later save it back, what exactly should happen? A naive approach would overwrite every field in the database with the current values in memory. But that strategy has problems: it can clobber concurrent changes to fields you never touched, and it sends more data over the wire than necessary.

Gault solves this with two complementary mechanisms: **Persistence** (knowing *whether* an instance exists in the database) and **StateTracker** (knowing *what has changed* since it was loaded). Together, they enable atomic saves that only update dirty fields.

## The problem atomic saves solve

Consider two application servers that load the same user document at roughly the same time:

```
Server A loads User(name="Alice", score=100)
Server B loads User(name="Alice", score=100)

Server A sets score = 150, then saves
Server B sets name = "Alicia", then saves
```

With a full-document overwrite, Server B's save would reset `score` back to 100, silently discarding Server A's update. With atomic saves, Server B's save only issues `$set: {name: "Alicia"}`, leaving `score` untouched.

## Persistence: "does this instance exist in the database?"

The `Persistence` class is a simple set that tracks which model instances have been persisted:

```python
class Persistence:
    def __init__(self):
        self._instances: WeakSet[Model] = WeakSet()

    def is_persisted(self, instance: Model) -> bool:
        return instance in self._instances

    def mark_persisted(self, instance: Model) -> None:
        self._instances.add(instance)

    def forget(self, instance: Model) -> None:
        self._instances.remove(instance)
```

An instance is marked as persisted in two situations:

1. **After a select/get/find** -- the instance was loaded from the database, so it clearly exists there.
2. **After an insert or save** -- the write succeeded, so the instance now exists.

The manager checks `is_persisted()` to decide how to handle the `atomic` flag during saves. If an instance has never been persisted, atomic mode is disabled -- there is no previous state in the database to protect, so all fields should be written.

### Why a WeakSet?

`Persistence` uses a `WeakSet` rather than a regular `set`. This means that when your application code drops all references to a model instance, the `Persistence` tracker does not prevent it from being garbage-collected. Without weak references, every instance ever loaded from the database would remain in memory for the lifetime of the manager -- a classic memory leak in long-running services.

```
                   Application code            Persistence
                   ================            ===========

    user = manager.get(User, ...)  ------+---> WeakSet { user }
                                         |
    del user  (or goes out of scope)     |
                                         v
                                    WeakSet { }   <-- automatically cleaned up
```

## StateTracker: "what has changed?"

The `StateTracker` records a snapshot of each instance's attribute values at the moment it is loaded or saved:

```python
class StateTracker:
    def __init__(self):
        self._states: WeakKeyDictionary[Model, Any] = WeakKeyDictionary()

    def snapshot(self, instance: Model) -> None:
        self._states[instance] = deepcopy(instance.__dict__)

    def get_dirty_fields(self, instance: Model) -> set[str]:
        dirty_fields = set()
        if snapshoted := self._states.get(instance):
            state = instance.__dict__
            for key, val in snapshoted.items():
                if state[key] != val:
                    dirty_fields.add(key)
        return dirty_fields
```

The snapshot is a `deepcopy` of the instance's `__dict__`. When the manager later needs to know which fields have changed, `get_dirty_fields()` compares the current `__dict__` against the snapshot, key by key.

Using `deepcopy` is essential: without it, mutable values (lists, dicts, embedded objects) would be shared between the snapshot and the live instance, and mutations would silently propagate to the snapshot, making it impossible to detect changes.

### The WeakKeyDictionary

Like `Persistence`, the state tracker uses weak references -- here, a `WeakKeyDictionary` keyed by the model instance. When the instance is garbage-collected, its snapshot is automatically discarded. The symmetry is intentional: both trackers have the same lifetime semantics, and neither can leak memory.

## The atomic save flow

When you call `manager.save(instance, atomic=True)`, the following sequence unfolds:

```
                     save(instance, atomic=True)
                              |
                              v
                 +---------------------------+
                 | Is instance persisted?    |
                 +---------------------------+
                      |              |
                     Yes             No
                      |              |
                      v              v
              atomic = True    atomic = False
                      |              |
                      v              v
            +-----------------------------+
            | Iterate over all fields     |
            | via mapper.iter_document()  |
            +-----------------------------+
                      |
          For each (model_field, db_field, value, pk):
                      |
              +-------+-------+--------+
              |               |        |
          pk == True    atomic and     otherwise
              |         not dirty      |
              v               |        v
         filter[db_field]     v     on_update[db_field]
          = {"$eq": value}  on_insert[db_field]   = value
                             = value
                              |
                              v
             +-------------------------------+
             | Build MongoDB update command  |
             +-------------------------------+
             | {                             |
             |   "$set": on_update,          |
             |   "$setOnInsert": on_insert   |
             | }                             |
             +-------------------------------+
                              |
                              v
             find_one_and_update(
               filter=filter,
               update=update,
               upsert=True
             )
                              |
                              v
             mark_persisted + snapshot
```

The key insight is the split between `$set` and `$setOnInsert`:

- **`$set`** contains fields that have changed (dirty fields) or, in non-atomic mode, all non-PK fields. These are always written, whether the document already exists or is being created for the first time.
- **`$setOnInsert`** contains fields that have *not* changed. These are only written if the `upsert` creates a new document. If the document already exists, these fields are left untouched -- preserving any concurrent modifications made by other processes.

The `upsert=True` parameter means the operation acts as an insert-or-update in a single atomic database call, eliminating the need for a separate "does this document exist?" check.

## How refresh works

Sometimes you need to pull the latest state from the database back into an in-memory instance -- for example, after another process has modified the document, or after a save with server-side defaults.

```python
manager.refresh(instance)
```

The refresh flow:

1. The mapper builds a filter from the instance's PK fields.
2. A `find_one` query fetches the current document from the collection.
3. The mapper creates a fresh model instance from the document.
4. The live instance's `__dict__` is replaced wholesale with the fresh instance's `__dict__`.
5. The instance is re-marked as persisted and a new snapshot is taken.

Step 4 is worth noting: rather than updating individual attributes, Gault replaces the entire `__dict__`. This guarantees that the refresh is complete -- no stale values can linger from the previous state. The same technique is used when `save(refresh=True)` is called, where the returned document from `find_one_and_update` is used to refresh the instance in the same operation.

## The lifecycle at a glance

```
  +------------------+         +--------------------+
  |  manager.select  | ------> | mark_persisted()   |
  |  manager.get     |         | snapshot()         |
  |  manager.find    |         +--------------------+
  +------------------+                  |
                                        v
                              Instance in use by app
                              (mutations happen here)
                                        |
                                        v
  +------------------+         +--------------------+
  |  manager.save    | ------> | get_dirty_fields() |
  |  (atomic=True)   |         | build $set / $setOnInsert
  +------------------+         | find_one_and_update|
                               | mark_persisted()   |
                               | snapshot()         |
                               +--------------------+
                                        |
                                        v
                              Instance continues in use
                              (new baseline for next save)
```

After a successful save, a fresh snapshot is taken. This resets the dirty-field baseline so that subsequent saves only consider changes made *after* the most recent save -- not changes accumulated since the original load.
