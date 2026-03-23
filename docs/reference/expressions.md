# Expressions

Aggregation expression operators for use in `$project`, `$set`, `$group`, `$match` (via `$expr`), and other pipeline stages. All expression classes live in `gault.expressions`.

Every expression class is a dataclass that implements `compile_expression(*, context) -> MongoPurExpression`. Expressions can be composed and nested.

```python
from gault.expressions import Add, Multiply, Cond, ToUpper
```

## Common patterns

Expressions can be used:

1. **Directly** -- instantiate the class:
   ```python
   Add("$price", "$tax")
   ```
2. **Via the fluent interface** on `Field.expr`, `AttributeSpec.expr`, or `Var`:
   ```python
   Field("price").expr.add("$tax")
   ```
3. **In pipeline stages**:
   ```python
   Pipeline().set({"total": Add("$price", "$tax")})
   Pipeline().project({"upper_name": ToUpper("$name")})
   ```

## Var

```python
@dataclass(frozen=True)
class Var(AsRef, AsAlias, ExpressionsInterface, FieldSortInterface, SubfieldInterface, ...)
```

A variable reference, e.g., `$$this`, `$$ROOT`, `$$CURRENT`, or user-defined variables in `$let`, `$map`, `$filter`.

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Variable name (without `$$` prefix). |

```python
from gault import Var

root = Var("ROOT")          # compiles to "$$ROOT"
this = Var("this")          # compiles to "$$this"
custom = Var("myVar")       # compiles to "$$myVar"
```

`Var` supports the full `ExpressionsInterface`, so you can chain expression methods:

```python
Var("this").expr.gt(10)     # {"$gt": ["$$this", 10]}
```

---

## Arithmetic operators

### Add

```python
class Add(ExpressionOperator)
```

Adds numbers together or adds numbers and a date.

| Parameter | Type | Description |
|---|---|---|
| `*inputs` | `NumberExpression` | Two or more expressions that resolve to numbers (or a number and a date). |

Raises `ValueError` if fewer than 2 inputs are provided.

```python
Add("$price", "$tax")
# Compiles to: {"$add": ["$price", "$tax"]}

Add("$a", "$b", "$c")
# Compiles to: {"$add": ["$a", "$b", "$c"]}
```

### Subtract

```python
@dataclass
class Subtract(ExpressionOperator)
```

Subtracts two numbers, two dates, or a date and a number.

| Parameter | Type | Description |
|---|---|---|
| `input1` | `NumberExpression \| DateExpression` | Left operand. |
| `input2` | `NumberExpression \| DateExpression` | Right operand. |

```python
Subtract("$total", "$discount")
# {"$subtract": ["$total", "$discount"]}
```

### Multiply

```python
class Multiply(ExpressionOperator)
```

Multiplies numbers together.

| Parameter | Type | Description |
|---|---|---|
| `*inputs` | `NumberExpression` | Two or more expressions. |

```python
Multiply("$price", "$quantity")
# {"$multiply": ["$price", "$quantity"]}
```

### Divide

```python
@dataclass
class Divide(ExpressionOperator)
```

Divides one number by another.

| Parameter | Type | Description |
|---|---|---|
| `dividende` | `NumberExpression` | Numerator. |
| `divisor` | `NumberExpression` | Denominator. |

```python
Divide("$total", "$count")
# {"$divide": ["$total", "$count"]}
```

### Mod

```python
@dataclass
class Mod(ExpressionOperator)
```

Returns the remainder of dividing two numbers.

| Parameter | Type | Description |
|---|---|---|
| `value1` | `NumberExpression` | Dividend. |
| `value2` | `NumberExpression` | Divisor. |

```python
Mod("$hours", 24)
# {"$mod": ["$hours", 24]}
```

### Abs

```python
@dataclass
class Abs(ExpressionOperator)
```

Returns the absolute value of a number.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | A numeric expression. |

```python
Abs("$delta")
# {"$abs": "$delta"}
```

### Ceil

```python
@dataclass
class Ceil(ExpressionOperator)
```

Returns the smallest integer greater than or equal to the specified number.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | A numeric expression. |

```python
Ceil("$price")
# {"$ceil": "$price"}
```

### Floor

```python
@dataclass
class Floor(ExpressionOperator)
```

Returns the largest integer less than or equal to the specified number.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | A numeric expression. |

```python
Floor("$price")
# {"$floor": "$price"}
```

### Round

```python
@dataclass
class Round(ExpressionOperator)
```

Rounds a number to a whole integer or to a specified decimal place.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `NumberExpression` | _(required)_ | The number to round. |
| `place` | `NumberExpression` | `0` | Decimal place to round to. |

```python
Round("$score", 2)
# {"$round": ["$score", 2]}
```

### Trunc

```python
@dataclass
class Trunc(ExpressionOperator)
```

Truncates a number to a whole integer or to a specified decimal place.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | The number to truncate. |
| `place` | `NumberExpression` | Decimal place. |

### Pow

```python
@dataclass
class Pow(ExpressionOperator)
```

Raises a number to the specified exponent.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | Base. |
| `exponent` | `NumberExpression` | Exponent. |

```python
Pow("$base", 2)
# {"$pow": ["$base", 2]}
```

### Sqrt

```python
@dataclass
class Sqrt(ExpressionOperator)
```

Calculates the square root.

| Parameter | Type | Description |
|---|---|---|
| `input` | `NumberExpression` | A non-negative numeric expression. |

### Exp

```python
@dataclass
class Exp(ExpressionOperator)
```

Raises Euler's number (e) to the specified exponent.

| Parameter | Type | Description |
|---|---|---|
| `exponent` | `NumberExpression` | The exponent. |

### Ln, Log, Log10

```python
@dataclass
class Ln(ExpressionOperator)   # Natural logarithm
class Log(ExpressionOperator)  # Log with specified base
class Log10(ExpressionOperator) # Base-10 logarithm
```

| Class | Parameters |
|---|---|
| `Ln` | `input: NumberExpression` |
| `Log` | `input: NumberExpression`, `base: NumberExpression` |
| `Log10` | `input: NumberExpression` |

---

## Comparison operators

### Eq

```python
@dataclass
class Eq(ExpressionOperator)
```

Returns `true` when two values are equivalent.

| Parameter | Type | Description |
|---|---|---|
| `lhs` | `AnyExpression` | Left operand. |
| `rhs` | `AnyExpression` | Right operand. |

```python
Eq("$status", "active")
# {"$eq": ["$status", "active"]}
```

### Ne

```python
@dataclass
class Ne(ExpressionOperator)
```

Returns `true` when two values are not equivalent.

| Parameter | Type | Description |
|---|---|---|
| `lhs` | `AnyExpression` | Left operand. |
| `rhs` | `AnyExpression` | Right operand. |

```python
Ne("$status", "deleted")
# {"$ne": ["$status", "deleted"]}
```

### Gt, Gte, Lt, Lte

```python
@dataclass
class Gt(ExpressionOperator)   # Greater than
class Gte(ExpressionOperator)  # Greater than or equal
class Lt(ExpressionOperator)   # Less than
class Lte(ExpressionOperator)  # Less than or equal
```

All take `lhs: AnyExpression` and `rhs: AnyExpression`.

```python
Gt("$age", 18)
# {"$gt": ["$age", 18]}

Lte("$score", 100)
# {"$lte": ["$score", 100]}
```

### Cmp

```python
@dataclass
class Cmp(ExpressionOperator)
```

Compares two values. Returns `-1`, `0`, or `1`.

| Parameter | Type | Description |
|---|---|---|
| `lhs` | `AnyExpression` | First value. |
| `rhs` | `AnyExpression` | Second value. |

```python
Cmp("$a", "$b")
# {"$cmp": ["$a", "$b"]}
```

### In

```python
@dataclass
class In(ExpressionOperator)
```

Returns `true` if a value is in an array.

| Parameter | Type | Description |
|---|---|---|
| `lhs` | `AnyExpression` | Value to search for. |
| `rhs` | `ArrayExpression` | Array to search in. |

```python
In("$status", ["active", "pending"])
# {"$in": ["$status", ["active", "pending"]]}
```

---

## String operators

### Concat

```python
class Concat(ExpressionOperator)
```

Concatenates strings.

| Parameter | Type | Description |
|---|---|---|
| `*inputs` | `StringExpression` | One or more string expressions. |

```python
Concat("$firstName", " ", "$lastName")
# {"$concat": ["$firstName", " ", "$lastName"]}
```

### SubStrBytes / SubStrCP

```python
@dataclass
class SubStrBytes(ExpressionOperator)  # By UTF-8 bytes
class SubStrCP(ExpressionOperator)     # By code points
```

| Parameter | Type | Description |
|---|---|---|
| `input` | `StringExpression` | The source string. |
| `start` | `NumberExpression` | Starting index. |
| `length` | `NumberExpression` | Number of bytes/code points. |

```python
SubStrBytes("$name", 0, 5)
# {"$substrBytes": ["$name", 0, 5]}
```

### ToLower

```python
@dataclass
class ToLower(ExpressionOperator)
```

Converts a string to lowercase.

| Parameter | Type | Description |
|---|---|---|
| `input` | `AnyExpression` | A string expression. |

```python
ToLower("$name")
# {"$toLower": "$name"}
```

### ToUpper

```python
@dataclass
class ToUpper(ExpressionOperator)
```

Converts a string to uppercase.

| Parameter | Type | Description |
|---|---|---|
| `input` | `AnyExpression` | A string expression. |

```python
ToUpper("$name")
# {"$toUpper": "$name"}
```

### Trim, Ltrim, Rtrim

```python
@dataclass
class Trim(ExpressionOperator)   # Both ends
class Ltrim(ExpressionOperator)  # Beginning
class Rtrim(ExpressionOperator)  # End
```

| Parameter | Type | Description |
|---|---|---|
| `input` | `StringExpression` | Source string. |
| `chars` | `StringExpression` | Characters to remove. |

```python
Trim("$name", chars=" ")
# {"$trim": {"input": "$name", "chars": " "}}
```

### Split

```python
@dataclass
class Split(ExpressionOperator)
```

Splits a string into an array by a delimiter.

| Parameter | Type | Description |
|---|---|---|
| `input` | `StringExpression` | Source string. |
| `delimiter` | `StringExpression` | Delimiter. |

### StrLenBytes / StrLenCP

```python
@dataclass
class StrLenBytes(ExpressionOperator)  # UTF-8 byte length
class StrLenCP(ExpressionOperator)     # Code point length
```

| Parameter | Type | Description |
|---|---|---|
| `input` | `StringExpression` | A string expression. |

### StrCaseCmp

```python
@dataclass
class StrCaseCmp(ExpressionOperator)
```

Case-insensitive string comparison.

| Parameter | Type | Description |
|---|---|---|
| `input1` | `StringExpression` | First string. |
| `input2` | `StringExpression` | Second string. |

### IndexOfBytes / IndexOfCP

```python
@dataclass
class IndexOfBytes(ExpressionOperator)
class IndexOfCP(ExpressionOperator)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `StringExpression` | _(required)_ | String to search. |
| `search` | `StringExpression` | _(required)_ | Substring to find. |
| `start` | `NumberExpression \| None` | `None` | Start index. |
| `end` | `NumberExpression \| None` | `None` | End index. |

### ReplaceOne / ReplaceAll

```python
@dataclass
class ReplaceOne(ExpressionOperator)  # First occurrence
class ReplaceAll(ExpressionOperator)  # All occurrences
```

| Parameter | Type | Description |
|---|---|---|
| `input` | `StringExpression` | Source string. |
| `find` | `StringExpression` | Substring to find. |
| `replacement` | `StringExpression` | Replacement string. |

### RegexFind / RegexFindAll / RegexMatch

```python
@dataclass
class RegexFind(ExpressionOperator)
class RegexFindAll(ExpressionOperator)
class RegexMatch(ExpressionOperator)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `StringExpression` | _(required)_ | String to search. |
| `regex` | `RegexExpression` | _(required)_ | Regular expression pattern. |
| `options` | `StringExpression \| None` | `None` | Regex options (e.g., `"i"`). |

---

## Array operators

### ArrayElemAt

```python
@dataclass
class ArrayElemAt(ExpressionOperator)
```

Returns the element at the specified array index.

| Parameter | Type | Description |
|---|---|---|
| `input` | `ArrayExpression` | An array. |
| `index` | `NumberExpression` | (keyword-only) Zero-based index. |

```python
ArrayElemAt("$tags", index=0)
# {"$arrayElemAt": ["$tags", 0]}
```

### ConcatArrays

```python
class ConcatArrays(ExpressionOperator)
```

Concatenates multiple arrays into one.

| Parameter | Type | Description |
|---|---|---|
| `*inputs` | `ArrayExpression` | Two or more arrays. |

```python
ConcatArrays("$arr1", "$arr2")
# {"$concatArrays": ["$arr1", "$arr2"]}
```

### Filter

```python
@dataclass
class Filter(ExpressionOperator)
```

Selects a subset of an array based on a condition.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `ArrayExpression` | _(required)_ | Source array. |
| `cond` | `BooleanExpression \| Callable` | _(required)_ | Condition to evaluate for each element. If a callable, receives `(Var, Context)`. |
| `var` | `PathLike \| None` | `None` | Variable name for current element (defaults to `"this"`). |
| `limit` | `int \| None` | `None` | Maximum number of elements. |

```python
Filter("$scores", cond=Gt(Var("this"), 50))
# {"$filter": {"input": "$scores", "cond": {"$gt": ["$$this", 50]}}}

# With callable
Filter("$scores", cond=lambda this, ctx: this.gt(50))
```

### Map

```python
@dataclass
class Map(ExpressionOperator)
```

Applies an expression to each element of an array.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `ArrayExpression` | _(required)_ | Source array. |
| `into` | `AnyExpression` | _(required)_ | Expression to apply. If callable, receives `(Var, Context)`. |
| `var` | `PathLike \| None` | `None` | Variable name for current element (defaults to `"this"`). |

```python
Map("$items", into=Multiply(Var("this"), 2))
# {"$map": {"input": "$items", "in": {"$multiply": ["$$this", 2]}}}
```

### Reduce

```python
@dataclass
class Reduce(ExpressionOperator)
```

Combines array elements into a single value.

| Parameter | Type | Description |
|---|---|---|
| `input` | `ArrayExpression` | Source array. |
| `initial_value` | `Value` | Starting value for the accumulator. |
| `into` | `AnyExpression` | Expression to apply (has access to `$$value` and `$$this`). |

```python
Reduce("$numbers", initial_value=0, into=Add(Var("value"), Var("this")))
```

### Size

```python
@dataclass
class Size(ExpressionOperator)
```

Returns the number of elements in an array.

| Parameter | Type | Description |
|---|---|---|
| `input` | `ArrayExpression` | An array expression. |

```python
Size("$tags")
# {"$size": "$tags"}
```

### Slice

```python
@dataclass
class Slice(ExpressionOperator)
```

Returns a subset of an array.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `ArrayExpression` | _(required)_ | Source array. |
| `n` | `NumberExpression` | _(required, kw)_ | Number of elements. |
| `position` | `NumberExpression \| None` | `None` _(kw)_ | Starting position. |

### IndexOfArray

```python
@dataclass
class IndexOfArray(ExpressionOperator)
```

Returns the index of the first occurrence of a value in an array.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `ArrayExpression` | _(required)_ | Array to search. |
| `search` | `AnyExpression` | _(required)_ | Value to find. |
| `start` | `NumberExpression \| None` | `None` | Start index. |
| `end` | `NumberExpression \| None` | `None` | End index. |

### ReverseArray

```python
@dataclass
class ReverseArray(ExpressionOperator)
```

Returns an array with elements in reverse order.

| Parameter | Type | Description |
|---|---|---|
| `input` | `ArrayExpression` | An array. |

### SortArray

```python
@dataclass
class SortArray(ExpressionOperator)
```

Sorts an array.

| Parameter | Type | Description |
|---|---|---|
| `input` | `ArrayExpression` | An array. |
| `sort_by` | `SortPayload` | Sort specification. |

### Zip

```python
@dataclass
class Zip(ExpressionOperator)
```

Transposes arrays.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `inputs` | `list[ArrayExpression]` | _(required)_ | Arrays to transpose. |
| `use_longest_length` | `bool \| None` | `None` | Pad shorter arrays. |
| `defaults` | `list[Value] \| None` | `None` | Default values for padding. |

### ArrayToObject / ObjectToArray

```python
@dataclass
class ArrayToObject(ExpressionOperator)  # Array -> document
class ObjectToArray(ExpressionOperator)  # Document -> array
```

Both take a single `input` parameter.

### Set operations

```python
class SetDifference(ExpressionOperator)     # Elements in first but not second
class SetEquals(ExpressionOperator)         # Same distinct elements (2+ arrays)
class SetIntersection(ExpressionOperator)   # Common elements (2+ arrays)
class SetIsSubset(ExpressionOperator)       # First is subset of second
class SetUnion(ExpressionOperator)          # Unique elements from all (2+ arrays)
class AllElementsTrue(ExpressionOperator)   # All elements are true
class AnyElementsTrue(ExpressionOperator)   # Any element is true
```

---

## Date operators

### DateAdd / DateSubtract

```python
@dataclass
class DateAdd(ExpressionOperator)
class DateSubtract(ExpressionOperator)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `start_date` | `DateExpression` | _(required)_ | Starting date. |
| `unit` | `DateUnit` | _(required)_ | `"year"`, `"quarter"`, `"month"`, `"week"`, `"day"`, `"hour"`, `"minute"`, `"second"`, `"millisecond"`. |
| `amount` | `NumberExpression` | _(required)_ | Number of units. |
| `timezone` | `TimezoneExpression \| None` | `None` | Olson timezone or UTC offset. |

```python
DateAdd("$createdAt", unit="day", amount=30)
# {"$dateAdd": {"startDate": "$createdAt", "unit": "day", "amount": 30}}
```

### DateDiff

```python
@dataclass
class DateDiff(ExpressionOperator)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `start_date` | `DateExpression` | _(required)_ | Start date. |
| `end_date` | `DateExpression` | _(required)_ | End date. |
| `unit` | `DateUnit` | _(required)_ | Unit of measurement. |
| `timezone` | `Timezone \| None` | `None` | Timezone. |
| `start_of_week` | `DayWeek \| None` | `None` | Day to start weeks. |

### DateFromParts

```python
@dataclass
class DateFromParts(ExpressionOperator)
```

Constructs a Date from constituent parts. All parameters are optional `NumberExpression` fields: `year`, `iso_week_year`, `month`, `iso_week`, `day`, `iso_day_of_week`, `hour`, `minute`, `second`, `millisecond`, `timezone`.

### DateFromString

```python
@dataclass
class DateFromString(ExpressionOperator)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `date_string` | `DateExpression` | _(required)_ | String to parse. |
| `format` | `str \| None` | `None` | Date format specification. |
| `timezone` | `Timezone \| None` | `None` | Timezone. |
| `on_error` | `AnyExpression \| None` | `None` | Fallback on error. |
| `on_null` | `AnyExpression \| None` | `None` | Fallback on null. |

### DateToParts / DateToString / DateTrunc

```python
@dataclass
class DateToParts(ExpressionOperator)    # Date -> parts document
class DateToString(ExpressionOperator)   # Date -> formatted string
class DateTrunc(ExpressionOperator)      # Truncate date to unit
```

### Date component extractors

All take `date: DateExpression` and optional `timezone: Timezone | None`:

| Class | Returns |
|---|---|
| `DayOfMonth` | Day of month (1-31) |
| `DayOfWeek` | Day of week (1=Sunday to 7=Saturday) |
| `DayOfYear` | Day of year (1-366) |
| `Hour` | Hour (0-23) |
| `Minute` | Minute (0-59) |
| `Second` | Second (0-59, 60 for leap seconds) |
| `Millisecond` | Millisecond (0-999) |
| `Month` | Month (1-12) |
| `Week` | Week of year (0-53) |
| `Year` | Year |
| `IsoDayOfWeek` | ISO weekday (1=Monday to 7=Sunday) |
| `IsoWeek` | ISO week (1-53) |
| `IsoWeekYear` | ISO year |

---

## Type operators

### Type

```python
@dataclass
class Type(ExpressionOperator)
```

Returns a string identifying the BSON type of the argument.

| Parameter | Type | Description |
|---|---|---|
| `input` | `AnyExpression` | Any expression. |

```python
Type("$value")
# {"$type": "$value"}
```

### Type conversion

| Class | Converts to | Parameter |
|---|---|---|
| `ToBool` | Boolean | `input: AnyExpression` |
| `ToDate` | Date | `input: AnyExpression` |
| `ToDecimal` | Decimal128 | `input: AnyExpression` |
| `ToDouble` | Double | `input: AnyExpression` |
| `ToInt` | Integer | `input: AnyExpression` |
| `ToLong` | Long | `input: AnyExpression` |
| `ToObjectId` | ObjectId | `input: AnyExpression` |
| `ToString` | String | `input: AnyExpression` |
| `ToUUID` | UUID | `input: AnyExpression` |
| `ToHashedIndexKey` | Hashed index key | `input: AnyExpression` |

```python
ToInt("$stringAge")
# {"$toInt": "$stringAge"}
```

### IsArray / IsNumber

```python
@dataclass
class IsArray(ExpressionOperator)
class IsNumber(ExpressionOperator)
```

Both take `input: AnyExpression` and return a boolean.

### BinarySize / BsonSize

```python
@dataclass
class BinarySize(ExpressionOperator)  # Size of string/binary in bytes
class BsonSize(ExpressionOperator)    # BSON size of document in bytes
```

---

## Conditional operators

### Cond

```python
@dataclass
class Cond(ExpressionOperator)
```

Evaluates a boolean expression and returns one of two values.

| Parameter | Type | Description |
|---|---|---|
| `when` | `BooleanExpression \| Predicate` | Condition. |
| `then` | `AnyExpression` | Value if true. |
| `otherwise` | `AnyExpression` | Value if false. |

```python
Cond(when=Gte("$score", 70), then="pass", otherwise="fail")
# {"$cond": {"if": {"$gte": ["$score", 70]}, "then": "pass", "else": "fail"}}
```

### IfNull

```python
class IfNull(ExpressionOperator)
```

Returns the first non-null value, or a replacement if all are null.

| Parameter | Type | Description |
|---|---|---|
| `*inputs` | `AnyExpression` | Expressions to evaluate in order. |

```python
IfNull("$nickname", "$name", "Anonymous")
# {"$ifNull": ["$nickname", "$name", "Anonymous"]}
```

### Switch

```python
@dataclass
class Switch(ExpressionOperator)
```

Evaluates a series of case expressions.

| Parameter | Type | Description |
|---|---|---|
| `branches` | `list[tuple[BooleanExpression, AnyExpression]]` | List of `(case, then)` tuples. |
| `default` | `AnyExpression` | Default value if no case matches. |

```python
Switch(
    branches=[
        (Gte("$score", 90), "A"),
        (Gte("$score", 80), "B"),
        (Gte("$score", 70), "C"),
    ],
    default="F",
)
# {"$switch": {"branches": [{"case": {"$gte": ["$score", 90]}, "then": "A"}, ...], "default": "F"}}
```

---

## Logical operators

### And / Or / Not

```python
class And(ExpressionOperator)   # All true
class Or(ExpressionOperator)    # Any true
class Not(ExpressionOperator)   # Boolean negation
```

`And` and `Or` accept `*inputs: AnyExpression`. `Not` takes a single `input: AnyExpression`.

Expressions also support Python operators `&`, `|`, and `~`:

```python
expr1 = Gt("$age", 18)
expr2 = Lt("$age", 65)
combined = expr1 & expr2    # And(expr1, expr2)
negated = ~expr1            # Not(expr1)
either = expr1 | expr2      # Or(expr1, expr2)
```

---

## Trigonometric operators

All take `input: NumberExpression`:

| Class | Description |
|---|---|
| `Sin` | Sine (radians) |
| `Cos` | Cosine (radians) |
| `Tan` | Tangent (radians) |
| `Sinh` | Hyperbolic sine |
| `Cosh` | Hyperbolic cosine |
| `Tanh` | Hyperbolic tangent |
| `Asin` | Inverse sine |
| `Acos` | Inverse cosine |
| `Atan` | Inverse tangent |
| `Asinh` | Inverse hyperbolic sine |
| `Acosh` | Inverse hyperbolic cosine |
| `Atanh` | Inverse hyperbolic tangent |
| `DegreesToRadians` | Convert degrees to radians |
| `RadiansToDegrees` | Convert radians to degrees |

`Atan2` takes `x: NumberExpression` and `y: NumberExpression`.

---

## Bitwise operators

| Class | Parameters | Description |
|---|---|---|
| `BitAnd` | `*inputs: NumberExpression` (2+) | Bitwise AND |
| `BitOr` | `*inputs: NumberExpression` (2+) | Bitwise OR |
| `BitXor` | `*inputs: NumberExpression` (1+) | Bitwise XOR |
| `BitNot` | `input: NumberExpression` | Bitwise NOT |

---

## Miscellaneous operators

| Class | Parameters | Description |
|---|---|---|
| `Literal` | `input: Value` | Returns a value without parsing (escape `$` strings). |
| `Let` | `variables: Mapping \| *Aliased`, `into: AnyExpression` | Binds variables for an expression. |
| `GetField` | `input: ObjectExpression`, `field: StringExpression` | Gets a field value from a document. |
| `SetField` | `input: ObjectExpression`, `field: StringExpression`, `value: AnyExpression` | Sets a field in a document. |
| `UnsetField` | `input: ObjectExpression`, `field: StringExpression` | Removes a field from a document. |
| `MergeObjects` | `*documents: ObjectExpression` | Merges multiple documents. |
| `Meta` | `keyword: "textScore" \| "indexKey"` | Returns document metadata. |
| `Rand` | _(no params)_ | Random float between 0 and 1. |
| `Range` | `start`, `end`, `step=1` | Generates a sequence of numbers. |
| `SampleRate` | `number: NumberExpression` | Randomly matches documents at a given rate. |
| `Sigmoid` | `input: NumberExpression`, `on_null: AnyExpression \| None` | Sigmoid function. |

---

## ExpressionsInterface (fluent API)

Both `Var` and `Field.expr` / `AttributeSpec.expr` provide the fluent `ExpressionsInterface`. This allows chaining expression methods directly on field references:

```python
from gault import Field, Var

# Arithmetic
Field("price").expr.add("$tax")            # Add("$price", "$tax")
Field("price").expr.multiply("$qty")       # Multiply("$price", "$qty")
Field("price").expr.subtract("$discount")  # Subtract("$price", "$discount")
Field("score").expr.abs()                  # Abs("$score")
Field("score").expr.ceil()                 # Ceil("$score")
Field("score").expr.floor()                # Floor("$score")
Field("score").expr.round(2)               # Round("$score", 2)

# Comparison
Field("age").expr.gt(18)                   # Gt("$age", 18)
Field("age").expr.eq(21)                   # Eq("$age", 21)

# String
Field("name").expr.to_lower()              # ToLower("$name")
Field("name").expr.to_upper()              # ToUpper("$name")
Field("name").expr.concat(" ", "$suffix")  # Concat("$name", " ", "$suffix")
Field("name").expr.trim(" ")               # Trim("$name", chars=" ")

# Array
Field("tags").expr.size()                  # Size("$tags")
Field("items").expr.filter(cond=...)       # Filter("$items", cond=...)
Field("items").expr.map(into=...)          # Map("$items", into=...)

# Date
Field("created").expr.year()               # Year("$created")
Field("created").expr.month()              # Month("$created")
Field("created").expr.day_of_week()        # DayOfWeek("$created")

# Type
Field("value").expr.type()                 # Type("$value")
Field("str_num").expr.to_int()             # ToInt("$str_num")
```
