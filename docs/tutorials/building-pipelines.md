# Building Aggregation Pipelines

In this tutorial we will build MongoDB aggregation pipelines with Gault's `Pipeline` API. We will filter, sort, group, and project data from an e-commerce orders dataset.

## Prerequisites

- Gault installed (`pip install gault`)
- A running MongoDB instance
- Familiarity with the basics from [Your First Schema](first-schema.md)

## Set up the schema

We will work with an `Order` schema representing e-commerce orders. Create a file called `pipeline_app.py`:

```python
import asyncio
from datetime import date
from pymongo import AsyncMongoClient
from gault import AsyncManager, Schema, Model, Field, Pipeline, configure
from gault.accumulators import Sum, Avg, Count


class Order(Schema, collection="orders"):
    order_id: Field[str] = configure(pk=True)
    customer: Field[str]
    product: Field[str]
    category: Field[str]
    quantity: Field[int]
    unit_price: Field[float]
    status: Field[str]
```

## Seed the data

Let's insert some sample orders:

```python
async def seed(manager: AsyncManager):
    orders = [
        Order(order_id="ORD-001", customer="Alice", product="Laptop",
              category="Electronics", quantity=1, unit_price=999.99, status="shipped"),
        Order(order_id="ORD-002", customer="Bob", product="Headphones",
              category="Electronics", quantity=2, unit_price=79.99, status="shipped"),
        Order(order_id="ORD-003", customer="Alice", product="Python Cookbook",
              category="Books", quantity=1, unit_price=45.00, status="delivered"),
        Order(order_id="ORD-004", customer="Charlie", product="Keyboard",
              category="Electronics", quantity=1, unit_price=129.99, status="pending"),
        Order(order_id="ORD-005", customer="Bob", product="Monitor",
              category="Electronics", quantity=1, unit_price=349.99, status="delivered"),
        Order(order_id="ORD-006", customer="Alice", product="Desk Lamp",
              category="Home", quantity=3, unit_price=24.99, status="delivered"),
        Order(order_id="ORD-007", customer="Charlie", product="Clean Code",
              category="Books", quantity=1, unit_price=39.99, status="shipped"),
        Order(order_id="ORD-008", customer="Bob", product="USB Cable",
              category="Electronics", quantity=5, unit_price=9.99, status="delivered"),
    ]
    for order in orders:
        await manager.insert(order)
    print(f"Seeded {len(orders)} orders.")
```

## Create a Pipeline

A `Pipeline` is built by chaining method calls. Each method adds a stage. The pipeline is immutable -- each call returns a new pipeline.

```python
    pipeline = Pipeline().match(Order.status == "shipped")
```

This creates a pipeline with a single `$match` stage. We can pass it directly to `manager.select()`:

```python
    async for order in manager.select(Order, pipeline):
        print(f"  {order.order_id}: {order.product} ({order.status})")
```

Expected output:

```
  ORD-001: Laptop (shipped)
  ORD-002: Headphones (shipped)
  ORD-007: Clean Code (shipped)
```

## match(), sort(), skip(), take()

Let's combine several stages. We want delivered electronics, sorted by price descending, limited to the top 2:

```python
    pipeline = (
        Pipeline()
        .match((Order.status == "delivered") & (Order.category == "Electronics"))
        .sort(Order.unit_price.desc())
        .skip(0)
        .take(2)
    )

    print("Top 2 delivered electronics:")
    async for order in manager.select(Order, pipeline):
        print(f"  {order.product}: ${order.unit_price}")
```

Expected output:

```
Top 2 delivered electronics:
  Monitor: $349.99
  USB Cable: $9.99
```

- `match()` accepts predicates built from schema fields, combined with `&` and `|`.
- `sort()` accepts `.asc()` or `.desc()` on any field.
- `skip()` and `take()` handle pagination.

## group() with accumulators

Now let's answer a business question: what is the total revenue per category?

Revenue for each order is `quantity * unit_price`. We will use `Sum` to aggregate.

```python
    pipeline = (
        Pipeline()
        .group(
            {"total_revenue": Sum("$unit_price"), "order_count": Count()},
            by="$category",
        )
    )
```

We cannot map this result to `Order` because the output shape is different. This is where **Model** comes in.

## Using Model for aggregation results

A `Model` is a non-persistent data class. It does not map to a collection -- it just describes the shape of aggregation output.

```python
class CategorySummary(Model):
    category: Field[str] = configure(db_alias="_id")
    total_revenue: Field[float]
    order_count: Field[int]
```

The group stage outputs `_id` for the group key. We use `db_alias="_id"` so that `category` reads from `_id` in the result.

Now we put it together:

```python
    pipeline = (
        Pipeline()
        .group(
            {"total_revenue": Sum("$unit_price"), "order_count": Count()},
            by="$category",
        )
        .sort({"total_revenue": -1})
    )

    print("Revenue by category:")
    async for summary in manager.select(CategorySummary, pipeline):
        print(f"  {summary.category}: ${summary.total_revenue:.2f} ({summary.order_count} orders)")
```

Expected output:

```
Revenue by category:
  Electronics: $1569.95 (5 orders)
  Books: $84.99 (2 orders)
  Home: $24.99 (1 orders)
```

Notice that we pass `CategorySummary` (a Model) to `manager.select()`. Gault maps the aggregation output documents to `CategorySummary` instances, but does not track persistence for them since they are not schemas.

## project() to shape output

`project()` reshapes documents. Let's create a summary view of each order showing just the customer, product, and a computed total.

First, define a Model for the projection:

```python
class OrderLine(Model):
    customer: Field[str]
    product: Field[str]
    line_total: Field[float]
```

Now build the pipeline:

```python
    pipeline = (
        Pipeline()
        .match(Order.status == "delivered")
        .project({
            "customer": True,
            "product": True,
            "line_total": {"$multiply": ["$quantity", "$unit_price"]},
        })
        .sort({"line_total": -1})
    )

    print("Delivered order lines:")
    async for line in manager.select(OrderLine, pipeline):
        print(f"  {line.customer} - {line.product}: ${line.line_total:.2f}")
```

Expected output:

```
Delivered order lines:
  Bob - Monitor: $349.99
  Alice - Desk Lamp: $74.97
  Bob - USB Cable: $49.95
  Alice - Python Cookbook: $45.00
```

## Combining group and project

Let's find the average order value per customer. We group by customer, compute the average unit price, then project to a clean shape.

```python
class CustomerStats(Model):
    name: Field[str] = configure(db_alias="_id")
    avg_price: Field[float]
    total_orders: Field[int]


async def customer_stats(manager: AsyncManager):
    pipeline = (
        Pipeline()
        .group(
            {"avg_price": Avg("$unit_price"), "total_orders": Count()},
            by="$customer",
        )
        .sort({"avg_price": -1})
    )

    print("Customer stats:")
    async for stat in manager.select(CustomerStats, pipeline):
        print(f"  {stat.name}: avg ${stat.avg_price:.2f} over {stat.total_orders} orders")
```

Expected output:

```
Customer stats:
  Alice: avg $356.66 over 3 orders
  Bob: avg $146.66 over 3 orders
  Charlie: avg $84.99 over 2 orders
```

## Pipeline.documents() for in-memory testing

You can test pipeline logic without a running MongoDB by using `Pipeline.documents()`. This injects documents directly into the pipeline using MongoDB's `$documents` stage.

```python
async def test_pipeline(manager: AsyncManager):
    pipeline = (
        Pipeline.documents(
            {"product": "A", "category": "X", "price": 10},
            {"product": "B", "category": "X", "price": 20},
            {"product": "C", "category": "Y", "price": 30},
            {"product": "D", "category": "Y", "price": 40},
        )
        .group(
            {"total": Sum("$price"), "count": Count()},
            by="$category",
        )
        .sort({"total": -1})
    )

    # Inspect the raw stages
    stages = pipeline.build()
    print("Pipeline stages:")
    for stage in stages:
        print(f"  {stage}")
```

Expected output:

```
Pipeline stages:
  {'$documents': [{'product': 'A', 'category': 'X', 'price': 10}, ...]}
  {'$group': {'_id': '$category', 'total': {'$sum': '$price'}, 'count': {'$count': {}}}}
  {'$sort': {'total': -1}}
```

You can also execute a `documents()` pipeline through the manager. Because the `$documents` stage is collection-independent, Gault runs it against the database directly:

```python
class GroupResult(Model):
    category: Field[str] = configure(db_alias="_id")
    total: Field[float]
    count: Field[int]


async def test_with_manager(manager: AsyncManager):
    pipeline = (
        Pipeline.documents(
            {"product": "A", "category": "X", "price": 10},
            {"product": "B", "category": "X", "price": 20},
            {"product": "C", "category": "Y", "price": 30},
            {"product": "D", "category": "Y", "price": 40},
        )
        .group(
            {"total": Sum("$price"), "count": Count()},
            by="$category",
        )
        .sort({"total": -1})
    )

    async for result in manager.select(GroupResult, pipeline):
        print(f"  {result.category}: total={result.total}, count={result.count}")
```

Expected output:

```
  Y: total=70.0, count=2
  X: total=30.0, count=2
```

This is useful for unit tests or prototyping pipelines before connecting them to real collections.

## Complete script

```python
import asyncio
from pymongo import AsyncMongoClient
from gault import AsyncManager, Schema, Model, Field, Pipeline, configure
from gault.accumulators import Sum, Avg, Count


class Order(Schema, collection="orders"):
    order_id: Field[str] = configure(pk=True)
    customer: Field[str]
    product: Field[str]
    category: Field[str]
    quantity: Field[int]
    unit_price: Field[float]
    status: Field[str]


class CategorySummary(Model):
    category: Field[str] = configure(db_alias="_id")
    total_revenue: Field[float]
    order_count: Field[int]


class OrderLine(Model):
    customer: Field[str]
    product: Field[str]
    line_total: Field[float]


class GroupResult(Model):
    category: Field[str] = configure(db_alias="_id")
    total: Field[float]
    count: Field[int]


async def main():
    client = AsyncMongoClient("mongodb://localhost:27017")
    db = client["shop"]
    manager = AsyncManager(db)

    # Seed data
    orders = [
        Order(order_id="ORD-001", customer="Alice", product="Laptop",
              category="Electronics", quantity=1, unit_price=999.99, status="shipped"),
        Order(order_id="ORD-002", customer="Bob", product="Headphones",
              category="Electronics", quantity=2, unit_price=79.99, status="shipped"),
        Order(order_id="ORD-003", customer="Alice", product="Python Cookbook",
              category="Books", quantity=1, unit_price=45.00, status="delivered"),
        Order(order_id="ORD-004", customer="Charlie", product="Keyboard",
              category="Electronics", quantity=1, unit_price=129.99, status="pending"),
        Order(order_id="ORD-005", customer="Bob", product="Monitor",
              category="Electronics", quantity=1, unit_price=349.99, status="delivered"),
        Order(order_id="ORD-006", customer="Alice", product="Desk Lamp",
              category="Home", quantity=3, unit_price=24.99, status="delivered"),
        Order(order_id="ORD-007", customer="Charlie", product="Clean Code",
              category="Books", quantity=1, unit_price=39.99, status="shipped"),
        Order(order_id="ORD-008", customer="Bob", product="USB Cable",
              category="Electronics", quantity=5, unit_price=9.99, status="delivered"),
    ]
    for order in orders:
        await manager.insert(order)

    # 1. match + sort + take
    pipeline = (
        Pipeline()
        .match((Order.status == "delivered") & (Order.category == "Electronics"))
        .sort(Order.unit_price.desc())
        .take(2)
    )
    print("Top 2 delivered electronics:")
    async for order in manager.select(Order, pipeline):
        print(f"  {order.product}: ${order.unit_price}")

    # 2. group with accumulators
    pipeline = (
        Pipeline()
        .group(
            {"total_revenue": Sum("$unit_price"), "order_count": Count()},
            by="$category",
        )
        .sort({"total_revenue": -1})
    )
    print("\nRevenue by category:")
    async for summary in manager.select(CategorySummary, pipeline):
        print(f"  {summary.category}: ${summary.total_revenue:.2f} ({summary.order_count} orders)")

    # 3. project with computed field
    pipeline = (
        Pipeline()
        .match(Order.status == "delivered")
        .project({
            "customer": True,
            "product": True,
            "line_total": {"$multiply": ["$quantity", "$unit_price"]},
        })
        .sort({"line_total": -1})
    )
    print("\nDelivered order lines:")
    async for line in manager.select(OrderLine, pipeline):
        print(f"  {line.customer} - {line.product}: ${line.line_total:.2f}")

    # 4. In-memory pipeline with Pipeline.documents()
    pipeline = (
        Pipeline.documents(
            {"product": "A", "category": "X", "price": 10},
            {"product": "B", "category": "X", "price": 20},
            {"product": "C", "category": "Y", "price": 30},
            {"product": "D", "category": "Y", "price": 40},
        )
        .group(
            {"total": Sum("$price"), "count": Count()},
            by="$category",
        )
        .sort({"total": -1})
    )
    print("\nIn-memory pipeline results:")
    async for result in manager.select(GroupResult, pipeline):
        print(f"  {result.category}: total={result.total}, count={result.count}")


asyncio.run(main())
```

## What's next

- Review the [Your First Schema](first-schema.md) tutorial if you skipped it.
- Explore the reference docs for the full list of pipeline stages, accumulators, and field predicates.
