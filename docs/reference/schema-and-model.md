# Schema and Model

Core classes for defining MongoDB document structures and mapping them to Python objects.

## Model

```python
class Model
```

Base class for defining MongoDB document shapes. Subclasses are automatically converted into dataclasses with `kw_only=True`. Fields declared as class-level annotations become `Attribute` descriptors.

`Model` subclasses are **read-only projections** -- they define a shape for querying but are not tied to a specific collection. Use `Schema` when you need full CRUD operations.

### Parameters (class keyword arguments)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `collection` | `str \| None` | `None` | MongoDB collection name. If provided, registers this model with the collection. |

### Example

```python
from gault import Model, configure

class UserSummary(Model, collection="users"):
    name: str
    email: str
```

When accessed on the class (not an instance), each field returns an `AttributeSpec` object that supports query predicates, sorting, and expression operations:

```python
# AttributeSpec supports predicates
predicate = UserSummary.name.eq("Alice")

# AttributeSpec supports sorting
sort_token = UserSummary.name.asc()

# AttributeSpec supports expressions
expr = UserSummary.name.expr.to_upper()
```

When accessed on an instance, each field returns the actual value:

```python
user = UserSummary(name="Alice", email="alice@example.com")
assert user.name == "Alice"
```

---

## Schema

```python
class Schema(Model, collection=...)
```

Extends `Model` to represent a **full collection schema**. The `collection` parameter is **required**. Schema classes are registered globally and can be retrieved with `get_schema()`.

Only `Schema` instances can be used with `insert()` and `save()` on the Manager.

### Parameters (class keyword arguments)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `collection` | `str` | Yes | MongoDB collection name. Raises `ValueError` if `None`. |

### Example

```python
from gault import Schema, configure

class User(Schema, collection="users"):
    id: str = configure(pk=True, db_alias="_id")
    name: str
    email: str
    age: int = configure(default=0)
```

### Raises

| Exception | Condition |
|---|---|
| `ValueError` | If `collection` is `None`. |

---

## Attribute

```python
class Attribute(Generic[T])
```

Descriptor that defines a field on a `Model` or `Schema`. Created automatically when a `Model` subclass is processed, but can also be used explicitly.

### Constructor

```python
Attribute(*, name: str | None = None, pk: bool = False, db_alias: str | None = None)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str \| None` | `None` | Python attribute name. Set automatically by `__set_name__`. |
| `pk` | `bool` | `False` | Whether this field is the primary key (used in `save()` and `refresh()`). |
| `db_alias` | `str \| None` | `None` | MongoDB document field name. Defaults to `name` if not set. |

### Descriptor behavior

| Access pattern | Returns |
|---|---|
| `MyModel.field` (class access) | `AttributeSpec[T]` -- supports predicates, sorting, expressions |
| `instance.field` (instance access) | `T` -- the actual field value |

### AttributeSpec

`AttributeSpec` is the object returned when accessing an `Attribute` on the class. It implements:

- **ConditionInterface** -- predicate methods: `eq()`, `ne()`, `gt()`, `gte()`, `lt()`, `lte()`, `in_()`, `nin()`, `exists()`, `type()`, `regex()`, `all()`, `elem_match()`, `size()`, `mod()`, geo operators, bitwise operators
- **FieldSortInterface** -- sorting methods: `asc()`, `desc()`, `by_score()`
- **SubfieldInterface** -- nested field access: `field("nested_name")`
- **NotInterface** -- negation: `not_` property returning a `NotProxy`
- **ExpressionInterface** -- expression access: `expr` property returning an `ExpressionProxy`
- **Python comparison operators** -- `==`, `!=`, `<`, `<=`, `>`, `>=` return `Predicate` objects

### Example

```python
class Product(Schema, collection="products"):
    id: str = configure(pk=True, db_alias="_id")
    name: str
    price: float
    tags: list[str] = configure(default_factory=list)

# Predicate via method
Product.price.gte(10.0)

# Predicate via Python operator
Product.price >= 10.0

# Sort token
Product.name.asc()

# Negation
Product.price.not_.gte(100.0)

# Expression proxy
Product.name.expr.to_lower()

# Subfield access
Product.tags.field("0")
```

---

## configure()

```python
def configure(*, default: Any = MISSING, **metadata: Unpack[AttributeMetadata]) -> Any
```

Helper function for declaring field metadata within a `Model` or `Schema`. Wraps `dataclasses.field()` with gault-specific metadata.

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `default` | `Any` | `MISSING` | Default value for the field. |
| `pk` | `bool` | _(not set)_ | Mark this field as the primary key. |
| `db_alias` | `str` | _(not set)_ | MongoDB document field name. Defaults to the Python attribute name. |

### Returns

A `dataclasses.field()` result suitable for use as a class-level default.

### Example

```python
class User(Schema, collection="users"):
    id: str = configure(pk=True, db_alias="_id")
    name: str
    email: str
    age: int = configure(default=0)
```

---

## get_schema()

```python
def get_schema(collection: str) -> type[Schema]
```

Retrieve the `Schema` class registered for a given collection name.

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `collection` | `str` | The MongoDB collection name. |

### Returns

`type[Schema]` -- The Schema class registered for that collection.

### Raises

| Exception | Condition |
|---|---|
| `KeyError` | If no Schema has been registered for the given collection. |

### Example

```python
schema_cls = get_schema("users")
# Returns the User class if User(Schema, collection="users") was defined
```

---

## get_collection()

```python
def get_collection(model: type[Model] | Model) -> str
```

Retrieve the MongoDB collection name associated with a Model or Schema class (or instance).

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `model` | `type[Model] \| Model` | A Model/Schema class or instance. |

### Returns

`str` -- The collection name.

### Raises

| Exception | Condition |
|---|---|
| `KeyError` | If the model was not registered with a collection name. |

### Example

```python
class User(Schema, collection="users"):
    id: str = configure(pk=True, db_alias="_id")
    name: str

assert get_collection(User) == "users"

user = User(id="1", name="Alice")
assert get_collection(user) == "users"
```

---

## Page

```python
@dataclass
class Page(Sequence[T])
```

A paginated result set returned by `Manager.paginate()` and `AsyncManager.paginate()`. Implements `collections.abc.Sequence`.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `instances` | `list[T]` | The items on the current page. |
| `total` | `int` | Total number of matching documents across all pages. |
| `page` | `int` | Current page number (1-based). |
| `per_page` | `int` | Number of items per page. |

### Methods

#### `with_(into: Callable[[T], U]) -> Page[U]`

Transform each item in the page using a mapping function. Returns a new `Page` with the same pagination metadata but transformed instances.

| Parameter | Type | Description |
|---|---|---|
| `into` | `Callable[[T], U]` | A function that transforms each item. |

**Returns:** `Page[U]`

#### Sequence interface

`Page` supports all `Sequence` operations:

- `page[0]` -- index access
- `page[1:3]` -- slicing
- `len(page)` -- number of items on this page
- `for item in page` -- iteration
- `reversed(page)` -- reverse iteration
- `item in page` -- containment check

### Example

```python
page = await manager.paginate(User, page=2, per_page=10)

print(page.total)       # 57
print(page.page)        # 2
print(page.per_page)    # 10
print(len(page))        # 10

# Transform to a different type
dto_page = page.with_(lambda u: {"name": u.name, "email": u.email})
```
