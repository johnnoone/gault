# Use Field Expressions

This guide covers the `.expr` property for building MongoDB `$expr` queries, and the `.not_` property for negating conditions.

## Setup

```python
from gault import Schema, configure, AsyncManager
from gault.predicates import Field

class Order(Schema, collection="orders"):
    id: Field[int] = configure(pk=True)
    price: Field[float]
    discount_price: Field[float]
    quantity: Field[int]
    total: Field[float]
    status: Field[str]
```

## The `.expr` property

Accessing `.expr` on a field returns an `ExpressionProxy` that wraps the field in MongoDB's `$expr` operator. This lets you use aggregation expression operators inside queries.

### Compare a field against a value

```python
Order.price.expr.gt(100)
# Compiles to: {"$expr": {"$gt": ["$price", 100]}}
```

### Compare two fields against each other

This is the primary use case -- standard query operators cannot compare fields directly.

```python
Order.price.expr.gt(Order.discount_price)
# Compiles to: {"$expr": {"$gt": ["$price", "$discount_price"]}}
```

Use it in a query:

```python
async for order in manager.select(Order, filter=Order.price.expr.gt(Order.discount_price)):
    print(f"Order {order.id}: price exceeds discount price")
```

### Available comparison methods

The proxy exposes the same comparisons as the predicate API, but operating at the expression level:

```python
Order.total.expr.eq(100)    # $eq
Order.total.expr.ne(0)      # $ne
Order.total.expr.gt(50)     # $gt
Order.total.expr.gte(50)    # $gte
Order.total.expr.lt(200)    # $lt
Order.total.expr.lte(200)   # $lte
```

### Arithmetic expressions

Chain arithmetic methods off `.expr` to build calculated conditions:

```python
# Check if total equals price * quantity
Order.total.expr.eq(Order.price.expr.multiply(Order.quantity))
# Compiles to: {"$expr": {"$eq": ["$total", {"$multiply": ["$price", "$quantity"]}]}}

# Addition
Order.total.expr.add(Order.tax)

# Subtraction
Order.price.expr.subtract(Order.discount_price)
```

### String expressions

```python
Order.status.expr.concat(" - processed")
```

### Using expressions with `Field`

Schema-free code works identically:

```python
Field("price").expr.gt(Field("discount_price"))
```

## The `.not_` property

The `.not_` property negates an operator using MongoDB's `$not`. This is different from `!=` (`$ne`) -- it inverts the result of the wrapped operator.

### Negate a comparison

```python
Order.quantity.not_.gte(10)
# Compiles to: {"quantity": {"$not": {"$gte": 10}}}
```

This matches documents where `quantity` is either less than 10 or the field does not exist.

### Negate a regex

```python
Order.status.not_.regex("^cancelled")
# Compiles to: {"status": {"$not": {"$regex": "^cancelled"}}}
```

### Callable form

You can also call `.not_` directly with an `Operator` instance:

```python
from gault.predicates import Gte

Order.quantity.not_(Gte(10))
# Same result as Order.quantity.not_.gte(10)
```

### When to use `.not_` vs `!=`

- `Order.status != "active"` produces `{"status": {"$ne": "active"}}` -- strict inequality check.
- `Order.status.not_.regex("^active")` produces `{"status": {"$not": {"$regex": "^active"}}}` -- logical negation of an operator.

Use `.not_` when you need to negate operators that have no direct inverse, such as `regex`, `mod`, `size`, or `exists`.

## Combining expressions with logical operators

Expression-based predicates compose with `&` and `|` like any other predicate:

```python
filter = Order.price.expr.gt(Order.discount_price) & (Order.quantity >= 5)
async for order in manager.select(Order, filter=filter):
    print(order.id)
```
