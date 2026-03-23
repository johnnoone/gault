# Track Dirty Fields

This guide covers how Gault tracks document state, detects modifications, and uses that information for efficient atomic saves.

## How state tracking works

When you load or save a document through a manager, two things happen:

1. **Persistence tracking** -- the instance is registered as persisted via `manager.persistence`.
2. **State snapshot** -- a deep copy of the instance's attributes is stored via `manager.state_tracker`.

These are automatic. You do not need to opt in.

```python
person = await manager.get(Person, filter=Person.id == 1)

# Both are now true:
manager.persistence.is_persisted(person)        # True
manager.state_tracker.get_dirty_fields(person)   # set() -- empty, nothing changed yet
```

A newly constructed instance that has not been saved or loaded is not tracked:

```python
new_person = Person(id=2, name="Alice", age=30)
manager.persistence.is_persisted(new_person)  # False
```

## Detecting dirty fields

After modifying an instance, call `get_dirty_fields()` to see which fields changed relative to the last snapshot:

```python
person = await manager.get(Person, filter=Person.id == 1)
person.name = "Updated Name"
person.age = 50

dirty = manager.state_tracker.get_dirty_fields(person)
# dirty == {"name", "age"}
```

The returned set contains Python field names (not database aliases).

## Atomic saves

Pass `atomic=True` to `save()` to update only the dirty fields. This is the primary consumer of dirty field tracking.

```python
person = await manager.get(Person, filter=Person.id == 1)
person.age = 51

await manager.save(person, atomic=True)
```

### What the generated update looks like

When `atomic=True` and the instance is already persisted, `save()` partitions fields into three categories:

| Category          | MongoDB operator  | Description                              |
|-------------------|-------------------|------------------------------------------|
| Primary key       | filter            | Used in the query filter to find the doc |
| Dirty fields      | `$set`            | Updated on both insert and update        |
| Unchanged fields  | `$setOnInsert`    | Written only if the document is new      |

For the example above, only `age` (mapped to its `db_alias`) goes into `$set`. All other non-PK fields go into `$setOnInsert`, so they are preserved if the document already exists.

### When atomic is ignored

`atomic=True` has no effect if the instance is **not** persisted (i.e., it was never loaded from the database or previously saved). In that case, all fields are sent as `$set`, behaving like a regular upsert.

```python
new_person = Person(id=3, name="Charlie", age=40)
# atomic=True has no effect here -- new_person is not persisted
await manager.save(new_person, atomic=True)
```

## Non-atomic saves

Without `atomic=True`, every non-PK field is placed in `$set` regardless of whether it changed. This is simpler but may overwrite concurrent modifications to fields you did not touch.

```python
await manager.save(person)  # All fields go to $set
```

## Refreshing after save

Pass `refresh=True` to `save()` to update the in-memory instance with the document returned by MongoDB after the upsert:

```python
await manager.save(person, refresh=True)
# person now reflects the exact state in the database,
# including any server-side defaults or modifications
```

After a refresh, the state snapshot is updated, so `get_dirty_fields()` returns an empty set again.

## Manual refresh

You can refresh an instance independently of a save:

```python
await manager.refresh(person)
# person.__dict__ is replaced with the latest database state
```

This re-reads the document using the primary key filter and raises `NotFound` if the document no longer exists.

## Resetting local changes

The state tracker can revert an instance to its last-snapshotted state:

```python
person.name = "Temporary change"
manager.state_tracker.reset(person)
# person.name is restored to its value at the time of the last snapshot
```

## Shared tracking across operations

`Persistence` and `StateTracker` are per-manager singletons (created lazily). All operations through the same manager share the same tracker, so a document loaded via `select()` and later passed to `save()` is correctly recognized as persisted.

If you need isolated tracking (e.g., in tests), construct a manager with explicit instances:

```python
from gault.managers import Persistence, StateTracker

manager = AsyncManager(
    database,
    persistence=Persistence(),
    state_tracker=StateTracker(),
)
```
