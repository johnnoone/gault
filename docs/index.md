# Gault

A lightweight Object Document Mapper (ODM) for MongoDB with Python type hints and state tracking.

## Why Gault?

- **Type-safe** — MongoDB documents with Python type hints and field aliasing
- **State tracking** — Automatic dirty field detection for atomic updates
- **Pipelines** — Fluent, immutable aggregation pipeline builder
- **Async & Sync** — Both `AsyncManager` and `Manager` for any codebase

## Quick example

```python
from gault import Schema, Field, configure, AsyncManager

class Person(Schema, collection="people"):
    id: Field[int] = configure(pk=True)
    name: Field[str]
    age: Field[int] = configure(db_alias="person_age")

manager = AsyncManager(database)

# Insert
person = Person(id=1, name="Alice", age=30)
await manager.insert(person)

# Query
person = await manager.get(Person, filter=Person.id == 1)

# Atomic update (only changed fields)
person.age = 31
await manager.save(person, atomic=True)
```

## Learn

<div class="grid cards" markdown>

-   **Tutorials** — Learn Gault step by step

    Start here if you're new. Build your first schema, insert documents, and query data.

    [:octicons-arrow-right-24: Get started](tutorials/index.md)

-   **How-to Guides** — Solve specific problems

    Filter documents, paginate results, track dirty fields, and compose pipelines.

    [:octicons-arrow-right-24: How-to guides](how-to/index.md)

-   **Reference** — Complete API documentation

    Every class, method, and parameter documented with examples.

    [:octicons-arrow-right-24: Reference](reference/index.md)

-   **Explanation** — Understand the design

    Why Schema vs Model? How does state tracking work? Pipeline architecture explained.

    [:octicons-arrow-right-24: Explanation](explanation/index.md)

</div>

## Installation

```bash
pip install gault
```

## Requirements

- Python >= 3.11
- PyMongo >= 4.15.4
