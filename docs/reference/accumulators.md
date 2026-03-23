# Accumulators

Accumulators are used within `Pipeline.group()` to compute aggregate values for each group. All accumulator classes live in `gault.accumulators` and are dataclasses that extend `Accumulator`.

```python
from gault.accumulators import Sum, Avg, Count, Min, Max, First, Last, Push, AddToSet
```

## Usage in group()

Accumulators are passed to `Pipeline.group()` as named expressions. Each accumulator must be aliased (given an output field name):

```python
from gault import Pipeline, Field
from gault.accumulators import Sum, Avg, Count

# Dict form
Pipeline().group(
    {"total_sales": Sum("$amount"), "avg_price": Avg("$price"), "doc_count": Count()},
    by="$category",
)

# Spread Aliased form (using .alias())
Pipeline().group(
    Sum("$amount").alias("total_sales"),
    Avg("$price").alias("avg_price"),
    Count().alias("doc_count"),
    by="$category",
)

# Group all documents (by=None)
Pipeline().group({"grand_total": Sum("$amount")}, by=None)
```

All accumulators support the `.alias(name)` method inherited from `AsAlias`, which wraps the accumulator in an `Aliased` container for use with the spread form.

---

## Accumulator (base class)

```python
class Accumulator(ABC, AsAlias)
```

Abstract base class for all accumulators. Subclasses must implement:

```python
def compile_expression(self, *, context: Context) -> MongoExpression
```

---

## Sum

```python
@dataclass
class Sum(Accumulator)
```

Returns the sum of numeric values. Ignores non-numeric values.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a number. Use `1` to count documents. |

```python
Sum("$amount")
# Compiles to: {"$sum": "$amount"}

Sum(1)
# Compiles to: {"$sum": 1}
```

**Example:**
```python
Pipeline().group({"total": Sum("$price")}, by="$category")
# {"$group": {"_id": "$category", "total": {"$sum": "$price"}}}
```

---

## Avg

```python
@dataclass
class Avg(Accumulator)
```

Returns the average of numeric values.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a number. |

```python
Avg("$score")
# {"$avg": "$score"}
```

**Example:**
```python
Pipeline().group({"avg_score": Avg("$score")}, by="$class")
```

---

## Count

```python
@dataclass
class Count(Accumulator)
```

Returns the number of documents in a group. Takes no parameters.

```python
Count()
# {"$count": {}}
```

**Example:**
```python
Pipeline().group({"total": Count()}, by="$status")
```

---

## Min

```python
@dataclass
class Min(Accumulator)
```

Returns the minimum value.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a comparable value. |

```python
Min("$price")
# {"$min": "$price"}
```

---

## Max

```python
@dataclass
class Max(Accumulator)
```

Returns the maximum value.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a comparable value. |

```python
Max("$price")
# {"$max": "$price"}
```

---

## First

```python
@dataclass
class First(Accumulator)
```

Returns the value from the first document in each group. Order depends on the preceding `$sort` stage.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression to evaluate. |

```python
First("$name")
# {"$first": "$name"}
```

**Example:**
```python
Pipeline().sort({"date": -1}).group({"latest_name": First("$name")}, by="$category")
```

---

## Last

```python
@dataclass
class Last(Accumulator)
```

Returns the value from the last document in each group.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression to evaluate. |

```python
Last("$name")
# {"$last": "$name"}
```

---

## FirstN

```python
@dataclass
class FirstN(Accumulator)
```

Returns the first `n` values in each group.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression to evaluate. |
| `n` | `int` | Number of values to return. |

```python
FirstN("$name", n=3)
# {"$firstN": {"input": "$name", "n": 3}}
```

---

## LastN

```python
@dataclass
class LastN(Accumulator)
```

Returns the last `n` values in each group.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression to evaluate. |
| `n` | `int` | Number of values to return. |

```python
LastN("$name", n=3)
# {"$lastN": {"input": "$name", "n": 3}}
```

---

## Push

```python
@dataclass
class Push(Accumulator)
```

Returns an array of all values for each group (including duplicates).

| Parameter | Type | Description |
|---|---|---|
| `input` | `AnyExpression` | Expression to evaluate. |

```python
Push("$tag")
# {"$push": "$tag"}
```

**Example:**
```python
Pipeline().group({"all_tags": Push("$tag")}, by="$category")
```

---

## AddToSet

```python
@dataclass
class AddToSet(Accumulator)
```

Returns an array of unique values for each group.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression to evaluate. |

```python
AddToSet("$tag")
# {"$addToSet": "$tag"}
```

**Example:**
```python
Pipeline().group({"unique_tags": AddToSet("$tag")}, by="$category")
```

---

## Top

```python
@dataclass
class Top(Accumulator)
```

Returns the top element within a group according to a sort order.

| Parameter | Type | Description |
|---|---|---|
| `sort_by` | `SortPayload` | Sort specification. |
| `output` | `AnyExpression \| list[AnyExpression]` | Expression(s) to return. |

```python
Top(sort_by={"score": -1}, output="$name")
# {"$top": {"sortBy": {"score": -1}, "output": "$name"}}
```

---

## TopN

```python
@dataclass
class TopN(Accumulator)
```

Returns the top `n` elements within a group.

| Parameter | Type | Description |
|---|---|---|
| `n` | `int` | Number of elements. |
| `sort_by` | `SortPayload` | Sort specification. |
| `output` | `AnyExpression \| list[AnyExpression]` | Expression(s) to return. |

```python
TopN(n=5, sort_by={"score": -1}, output="$name")
# {"$topN": {"n": 5, "sortBy": {"score": -1}, "output": "$name"}}
```

---

## Bottom

```python
@dataclass
class Bottom(Accumulator)
```

Returns the bottom element within a group according to a sort order.

| Parameter | Type | Description |
|---|---|---|
| `sort_by` | `SortPayload` | Sort specification. |
| `output` | `AnyExpression \| list[AnyExpression]` | Expression(s) to return. |

```python
Bottom(sort_by={"score": 1}, output="$name")
# {"$bottom": {"sortBy": {"score": 1}, "output": "$name"}}
```

---

## BottomN

```python
@dataclass
class BottomN(Accumulator)
```

Returns the bottom `n` elements within a group.

| Parameter | Type | Description |
|---|---|---|
| `n` | `int` | Number of elements. |
| `sort_by` | `SortPayload` | Sort specification. |
| `output` | `AnyExpression \| list[AnyExpression]` | Expression(s) to return. |

```python
BottomN(n=3, sort_by={"score": 1}, output=["$name", "$score"])
# {"$bottomN": {"n": 3, "sortBy": {"score": 1}, "output": ["$name", "$score"]}}
```

---

## MinN

```python
@dataclass
class MinN(Accumulator)
```

Returns the `n` minimum valued elements within a group.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression to evaluate. |
| `n` | `int` | Number of minimum values. |

```python
MinN("$price", n=3)
# {"$minN": {"input": "$price", "n": 3}}
```

---

## MaxN

```python
@dataclass
class MaxN(Accumulator)
```

Returns the `n` maximum valued elements within a group.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression to evaluate. |
| `n` | `int` | Number of maximum values. |

```python
MaxN("$price", n=3)
# {"$maxN": {"input": "$price", "n": 3}}
```

---

## Median

```python
@dataclass
class Median(Accumulator)
```

Returns an approximation of the median value. Uses the `"approximate"` method.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a number. |

```python
Median("$score")
# {"$median": {"input": "$score", "method": "approximate"}}
```

---

## Percentile

```python
@dataclass
class Percentile(Accumulator)
```

Returns an approximation of percentile values. Uses the `"approximate"` method.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a number. |
| `p` | `list[float]` | Percentile values between 0.0 and 1.0 inclusive. |

```python
Percentile("$score", p=[0.25, 0.5, 0.75])
# {"$percentile": {"input": "$score", "p": [0.25, 0.5, 0.75], "method": "approximate"}}
```

---

## StdDevPop

```python
@dataclass
class StdDevPop(Accumulator)
```

Returns the population standard deviation of the input values.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a number. |

```python
StdDevPop("$score")
# {"$stdDevPop": "$score"}
```

---

## StdDevSamp

```python
@dataclass
class StdDevSamp(Accumulator)
```

Returns the sample standard deviation of the input values.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Expression that resolves to a number. |

```python
StdDevSamp("$score")
# {"$stdDevSamp": "$score"}
```

---

## MergeObjects

```python
@dataclass
class MergeObjects(Accumulator)
```

Combines multiple documents into a single document. When used as a group accumulator, merges all documents in the group.

| Parameter | Type | Description |
|---|---|---|
| `input` | `ObjectExpression` | Expression that resolves to a document. |

```python
MergeObjects("$metadata")
# {"$mergeObjects": "$metadata"}
```

**Example:**
```python
Pipeline().group({"combined": MergeObjects("$details")}, by="$category")
```

---

## Quick reference table

| Accumulator | MongoDB operator | Parameters | Description |
|---|---|---|---|
| `Sum` | `$sum` | `input` | Sum of numeric values |
| `Avg` | `$avg` | `input` | Average of numeric values |
| `Count` | `$count` | _(none)_ | Document count |
| `Min` | `$min` | `input` | Minimum value |
| `Max` | `$max` | `input` | Maximum value |
| `First` | `$first` | `input` | First value in group |
| `Last` | `$last` | `input` | Last value in group |
| `FirstN` | `$firstN` | `input`, `n` | First N values |
| `LastN` | `$lastN` | `input`, `n` | Last N values |
| `Push` | `$push` | `input` | Array of all values |
| `AddToSet` | `$addToSet` | `input` | Array of unique values |
| `Top` | `$top` | `sort_by`, `output` | Top element by sort |
| `TopN` | `$topN` | `n`, `sort_by`, `output` | Top N elements by sort |
| `Bottom` | `$bottom` | `sort_by`, `output` | Bottom element by sort |
| `BottomN` | `$bottomN` | `n`, `sort_by`, `output` | Bottom N elements by sort |
| `MinN` | `$minN` | `input`, `n` | N minimum values |
| `MaxN` | `$maxN` | `input`, `n` | N maximum values |
| `Median` | `$median` | `input` | Approximate median |
| `Percentile` | `$percentile` | `input`, `p` | Approximate percentiles |
| `StdDevPop` | `$stdDevPop` | `input` | Population std deviation |
| `StdDevSamp` | `$stdDevSamp` | `input` | Sample std deviation |
| `MergeObjects` | `$mergeObjects` | `input` | Merge documents |
