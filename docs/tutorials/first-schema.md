# Your First Schema

In this tutorial we will install Gault, define a schema mapped to a MongoDB collection, insert a document, query it back, modify it, and save the changes. By the end you will understand the core workflow of the library.

## Prerequisites

- Python 3.11 or later
- A running MongoDB instance (local or remote)

## Install Gault

```bash
pip install gault
```

Gault depends on PyMongo, which will be installed automatically.

## Define a Schema

A **Schema** maps a Python class to a MongoDB collection. We will model a `Book` stored in a `"books"` collection.

Create a file called `app.py`:

```python
from gault import Schema, Field, configure

class Book(Schema, collection="books"):
    isbn: Field[str] = configure(pk=True)
    title: Field[str]
    author: Field[str]
    year: Field[int]
    price: Field[float] = configure(db_alias="retail_price")
```

Let's break down what we wrote:

- `Schema` tells Gault this class is a persistent document backed by a real MongoDB collection.
- `collection="books"` is the name of the MongoDB collection.
- `configure(pk=True)` marks `isbn` as the primary key. Gault uses it to identify documents during save operations.
- `configure(db_alias="retail_price")` means the `price` field is stored as `retail_price` in MongoDB. In Python we use `book.price`; in the database the column is `retail_price`.
- Every other field is stored under its Python name.

> For a deeper explanation of Schema vs Model and field configuration, see the explanation docs.

## Connect to MongoDB

We need a PyMongo `AsyncDatabase` and a Gault `AsyncManager`. Add the following to `app.py`:

```python
import asyncio
from pymongo import AsyncMongoClient
from gault import AsyncManager

async def main():
    client = AsyncMongoClient("mongodb://localhost:27017")
    db = client["library"]
    manager = AsyncManager(db)

asyncio.run(main())
```

The `AsyncManager` is the central object we use for all database operations: inserting, querying, and saving.

## Insert a document

Let's insert our first book. Add this inside the `main` function:

```python
    book = Book(
        isbn="978-0-13-468599-1",
        title="The Pragmatic Programmer",
        author="David Thomas",
        year=2019,
        price=49.99,
    )
    await manager.insert(book)
    print(f"Inserted: {book.title}")
```

Run the script:

```bash
python app.py
```

Expected output:

```
Inserted: The Pragmatic Programmer
```

The document is now in MongoDB. If you inspect the collection you will see the field `retail_price` instead of `price`, because of the `db_alias` we configured.

## Query with find() and get()

`find()` returns a single document or `None`. `get()` returns a single document or raises `NotFound`.

```python
    # find() -- returns None if not found
    result = await manager.find(Book, Book.isbn == "978-0-13-468599-1")
    print(result)
    # Book(isbn='978-0-13-468599-1', title='The Pragmatic Programmer', ...)

    # get() -- raises NotFound if missing
    from gault import NotFound

    try:
        missing = await manager.get(Book, Book.isbn == "000-0-00-000000-0")
    except NotFound:
        print("Book not found!")
```

Expected output:

```
Book(isbn='978-0-13-468599-1', title='The Pragmatic Programmer', author='David Thomas', year=2019, price=49.99)
Book not found!
```

Notice how we filter using `Book.isbn == "978-0-13-468599-1"`. Gault turns this Python expression into a MongoDB query automatically.

## Query with select()

`select()` returns an async iterator of all matching documents. Let's insert a few more books first and then query them.

```python
    await manager.insert(Book(
        isbn="978-0-596-51774-8",
        title="JavaScript: The Good Parts",
        author="Douglas Crockford",
        year=2008,
        price=29.99,
    ))
    await manager.insert(Book(
        isbn="978-0-13-235088-4",
        title="Clean Code",
        author="Robert C. Martin",
        year=2008,
        price=39.99,
    ))

    # Select all books from 2008
    async for book in manager.select(Book, Book.year == 2008):
        print(f"  {book.title} ({book.year})")
```

Expected output:

```
  JavaScript: The Good Parts (2008)
  Clean Code (2008)
```

You can combine conditions with `&` (and) and `|` (or):

```python
    # Books from 2008 that cost less than 35
    filter = (Book.year == 2008) & (Book.price < 35.00)
    async for book in manager.select(Book, filter):
        print(f"  {book.title} - ${book.price}")
```

Expected output:

```
  JavaScript: The Good Parts - $29.99
```

You can also use `skip` and `take` for pagination:

```python
    async for book in manager.select(Book, skip=0, take=2):
        print(f"  {book.title}")
```

## Modify and save with atomic=True

Now let's update a book's price. First we fetch it, then we modify it, then we save.

```python
    book = await manager.get(Book, Book.isbn == "978-0-13-468599-1")
    print(f"Before: {book.price}")

    book.price = 44.99
    await manager.save(book, atomic=True)
    print(f"After: {book.price}")
```

Expected output:

```
Before: 49.99
After: 44.99
```

The `atomic=True` flag is important. It tells Gault to only send the fields that actually changed to MongoDB. In this case, only `retail_price` is updated; `title`, `author`, and `year` are left untouched. This minimizes race conditions when multiple processes write to the same document.

Without `atomic=True`, every field is written on every save.

## Understanding persistence tracking

Gault tracks two things behind the scenes:

1. **Persistence** -- whether a document instance has been loaded from or saved to the database.
2. **Dirty fields** -- which fields have been modified since the last snapshot.

You can inspect these directly:

```python
    # Load a book from the database
    book = await manager.get(Book, Book.isbn == "978-0-13-468599-1")

    # It is marked as persisted
    print(manager.persistence.is_persisted(book))  # True

    # No fields are dirty yet
    print(manager.state_tracker.get_dirty_fields(book))  # set()

    # Modify a field
    book.title = "The Pragmatic Programmer, 20th Anniversary Edition"

    # Now 'title' is dirty
    print(manager.state_tracker.get_dirty_fields(book))  # {'title'}

    # Save with atomic=True -- only 'title' is sent to MongoDB
    await manager.save(book, atomic=True)

    # After saving, the snapshot is updated; no fields are dirty
    print(manager.state_tracker.get_dirty_fields(book))  # set()
```

A brand-new instance that has never been saved is not persisted:

```python
    new_book = Book(
        isbn="978-0-00-000000-0",
        title="Unpublished",
        author="Nobody",
        year=2025,
        price=0.0,
    )
    print(manager.persistence.is_persisted(new_book))  # False

    await manager.save(new_book)
    print(manager.persistence.is_persisted(new_book))  # True
```

> For a detailed explanation of how atomic saves, `$set`, and `$setOnInsert` work together, see the explanation docs.

## Complete script

Here is the full `app.py` for reference:

```python
import asyncio
from pymongo import AsyncMongoClient
from gault import AsyncManager, Schema, Field, configure, NotFound


class Book(Schema, collection="books"):
    isbn: Field[str] = configure(pk=True)
    title: Field[str]
    author: Field[str]
    year: Field[int]
    price: Field[float] = configure(db_alias="retail_price")


async def main():
    client = AsyncMongoClient("mongodb://localhost:27017")
    db = client["library"]
    manager = AsyncManager(db)

    # Insert
    book = Book(
        isbn="978-0-13-468599-1",
        title="The Pragmatic Programmer",
        author="David Thomas",
        year=2019,
        price=49.99,
    )
    await manager.insert(book)
    print(f"Inserted: {book.title}")

    # Find
    result = await manager.find(Book, Book.isbn == "978-0-13-468599-1")
    print(result)

    # Get (raises NotFound)
    try:
        await manager.get(Book, Book.isbn == "000-0-00-000000-0")
    except NotFound:
        print("Book not found!")

    # Select
    await manager.insert(Book(
        isbn="978-0-596-51774-8",
        title="JavaScript: The Good Parts",
        author="Douglas Crockford",
        year=2008,
        price=29.99,
    ))
    await manager.insert(Book(
        isbn="978-0-13-235088-4",
        title="Clean Code",
        author="Robert C. Martin",
        year=2008,
        price=39.99,
    ))

    async for book in manager.select(Book, Book.year == 2008):
        print(f"  {book.title} ({book.year})")

    # Modify and save
    book = await manager.get(Book, Book.isbn == "978-0-13-468599-1")
    book.price = 44.99
    await manager.save(book, atomic=True)
    print(f"Updated price: {book.price}")

    # Persistence tracking
    print(manager.persistence.is_persisted(book))  # True
    print(manager.state_tracker.get_dirty_fields(book))  # set()


asyncio.run(main())
```

## What's next

- [Building Aggregation Pipelines](building-pipelines.md) -- learn to group, sort, and reshape data.
