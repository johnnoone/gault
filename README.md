# Gault

A lightweight Object Document Mapper (ODM) for MongoDB with Python type hints and state tracking.

## Features

- Type-safe MongoDB documents with Python type hints
- Field aliasing for database column mapping
- Query operators with Pythonic syntax
- Async and sync managers for CRUD operations
- Aggregation pipeline support with fluent API
- Automatic state tracking and dirty field detection
- Atomic updates with persistence tracking

## Installation

```bash
pip install gault
```

## Quick Start

```python
from gault import Schema, Model, Field, configure, AsyncManager

# Schema: Persistent documents mapped to MongoDB collections
class Person(Schema, collection="people"):
    id: Field[int] = configure(pk=True)
    name: Field[str]
    age: Field[int] = configure(db_alias="person_age")

# Model: Non-persistent data classes (projections, view models, etc.)
class PersonSummary(Model):
    name: Field[str]
    total: Field[int]

# Create manager
manager = AsyncManager(database)

# Query and modify
person = await manager.get(Person, filter=Person.id == 1)
person.age = 43
await manager.save(person, atomic=True)  # Only updates dirty fields
```

## Querying

```python
# Comparison operators
Person.age >= 18
Person.id.in_([1, 2, 3])

# Logical operators
filter = (Person.age >= 18) & (Person.name == "Alice")
filter = (Person.name == "Alice") | (Person.name == "Bob")
filter = ~(Person.age < 18)

# Field expressions
Person.score.expr.gt(42)
Person.price.expr.gt(Person.discount_price)
```

## Aggregation Pipelines

```python
from gault import Pipeline
from gault.accumulators import Sum, Avg

pipeline = (
    Pipeline()
    .match(Person.age >= 18)
    .group({"total": Sum(1), "avg_age": Avg("$age")}, by="$name")
    .sort({"total": -1})
    .take(10)
)

async for result in manager.select(PersonSummary, pipeline):
    print(result.name, result.total)
```

## Persistence & Dirty Fields

```python
person = await manager.get(Person, filter=Person.id == 1)
person.name = "New Name"
person.age = 50

# Only updates changed fields
await manager.save(person, atomic=True)
```

## Requirements

- Python >= 3.11
- PyMongo >= 4.15.4

## Documentation

Full documentation available at **[johnnoone.github.io/gault](https://johnnoone.github.io/gault/)**.

## License

MIT
