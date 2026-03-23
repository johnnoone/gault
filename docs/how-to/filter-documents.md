# Filter Documents

This guide covers how to build filters for querying MongoDB documents through Gault's type-safe predicate API.

## Setup

All examples assume:

```python
from gault import Schema, configure, AsyncManager, Pipeline
from gault.predicates import Field

class Product(Schema, collection="products"):
    id: Field[int] = configure(pk=True)
    name: Field[str]
    price: Field[float]
    category: Field[str]
    stock: Field[int]
```

## Comparison operators

Use Python operators directly on schema fields or `Field` objects:

```python
# Equality / inequality
Product.price == 9.99
Product.price != 9.99

# Ordering
Product.price < 50
Product.price <= 50
Product.price > 10
Product.price >= 10
```

These return `Predicate` objects that you pass to manager methods:

```python
results = manager.select(Product, filter=Product.price >= 10)
```

## Inclusion with `in_()` and `nin()`

Match a field against a set of values:

```python
Product.category.in_("electronics", "books", "toys")
Product.category.nin("clothing", "food")
```

Both accept either positional arguments or a single list:

```python
allowed = ["electronics", "books"]
Product.category.in_(*allowed)
```

## Logical operators

Combine predicates with `&` (AND), `|` (OR), and `~` (NOR/invert):

```python
# AND -- both conditions must match
filter = (Product.price >= 10) & (Product.price <= 100)

# OR -- either condition matches
filter = (Product.category == "electronics") | (Product.category == "books")

# Invert an OR into NOR
filter = ~((Product.category == "electronics") | (Product.category == "books"))
```

Parentheses matter -- wrap each sub-expression before combining.

## Combining multiple filters

`&` chains flatten automatically, so you can build filters incrementally:

```python
base = Product.stock > 0
filtered = base & (Product.price < 100)
filtered = filtered & (Product.category == "electronics")
# Produces a single $and with three conditions
```

## Passing filters to manager methods

Every manager query method accepts a `filter` parameter:

```python
# Single document
product = await manager.get(Product, filter=Product.id == 42)

# Optional single document
product = await manager.find(Product, filter=Product.name == "Widget")

# Iteration
async for product in manager.select(Product, filter=Product.price < 20):
    print(product.name)

# With skip/take
async for product in manager.select(Product, filter=Product.stock > 0, skip=10, take=5):
    print(product.name)
```

## Using `Field` for schema-free queries

When you don't have a Schema class, use `Field` from `gault.predicates`:

```python
from gault.predicates import Field

filter = Field("price").gte(10) & Field("category").in_("electronics", "books")
pipeline = Pipeline().match(filter)
```

`Field` supports the same methods as schema attributes: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in_`, `nin`, `exists`, `regex`, `size`, `mod`, `type`, and more.

## Raw dict filters

Pass a plain MongoDB query dict when you need to bypass the predicate API:

```python
# Dict filter
product = await manager.find(Product, filter={"price": {"$gte": 10}})

# Raw aggregation stages
results = manager.select(Product, filter=[
    {"$match": {"category": "electronics"}},
    {"$sort": {"price": -1}},
    {"$limit": 5},
])
```

## Additional query operators

Beyond comparisons, fields expose specialized operators:

```python
# Field existence
Product.category.exists(True)

# Regex matching
Product.name.regex("^Widget", options="i")

# Array size
Product.tags.size(3)

# Modulo
Product.stock.mod(10, 0)  # stock divisible by 10

# BSON type check
Product.price.type("double")
```
