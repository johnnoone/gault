# Paginate Results

This guide covers how to retrieve paged result sets using `manager.paginate()` and work with the returned `Page` object.

## Setup

```python
from gault import Schema, configure, AsyncManager

class Article(Schema, collection="articles"):
    id: Field[int] = configure(pk=True)
    title: Field[str]
    author: Field[str]
    published: Field[bool]
```

## Basic pagination

Call `paginate()` with a model and optional filter. It returns a `Page` object:

```python
page = await manager.paginate(Article, filter=Article.published == True, page=1, per_page=20)
```

Parameters:

| Parameter  | Default | Description                    |
|------------|---------|--------------------------------|
| `model`    | --      | The model class to query       |
| `filter`   | `None`  | Predicate, Pipeline, or dict   |
| `page`     | `1`     | 1-based page number            |
| `per_page` | `10`    | Number of items per page       |
| `sort_by`  | `None`  | Sort specification             |

## The `Page` object

`Page` is a `Sequence` -- it holds results plus pagination metadata.

### Metadata attributes

```python
page.total     # Total number of matching documents across all pages
page.page      # Current page number
page.per_page  # Items per page
len(page)      # Number of items on this page (may be < per_page on the last page)
```

### Iterating results

`Page` implements `__iter__`, `__getitem__`, and `__len__`:

```python
# Iterate
for article in page:
    print(article.title)

# Index access
first = page[0]

# Slice
subset = page[2:5]

# Reverse
for article in reversed(page):
    print(article.title)

# Membership
if some_article in page:
    print("Found")
```

## Sorting

Pass `sort_by` to control ordering. Use field `.asc()` / `.desc()` methods or a dict:

```python
page = await manager.paginate(
    Article,
    filter=Article.published == True,
    page=2,
    per_page=10,
    sort_by=Article.title.asc(),
)
```

Multiple sort keys:

```python
page = await manager.paginate(
    Article,
    page=1,
    per_page=25,
    sort_by=[Article.author.asc(), Article.title.asc()],
)
```

Dict form:

```python
page = await manager.paginate(Article, sort_by={"title": 1, "author": -1})
```

## Transforming results with `Page.with_()`

`Page.with_()` maps each instance through a callable, returning a new `Page` with the same metadata but transformed items:

```python
from dataclasses import dataclass

@dataclass
class ArticleDTO:
    title: str
    author: str

dto_page = page.with_(lambda a: ArticleDTO(title=a.title, author=a.author))

# dto_page.total, dto_page.page, dto_page.per_page are preserved
for dto in dto_page:
    print(dto.title)
```

This is useful for converting domain models to API response objects without re-querying.

## Computing total pages

`Page` does not provide a `total_pages` property, but it is straightforward to compute:

```python
import math

total_pages = math.ceil(page.total / page.per_page)
```

## Pagination with Pipeline filters

You can pass a `Pipeline` as the filter -- the pagination stages are appended after your pipeline stages:

```python
from gault import Pipeline

pipeline = Pipeline().match(Article.published == True)
page = await manager.paginate(Article, filter=pipeline, page=3, per_page=10)
```

## Sync manager

The synchronous `Manager` has the same `paginate()` signature and returns the same `Page` type:

```python
page = manager.paginate(Article, page=1, per_page=20)
```
