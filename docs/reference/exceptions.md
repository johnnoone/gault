# Exceptions

All exceptions raised by gault. Import from the top-level package or from their respective submodules.

```python
from gault import NotFound, Forbidden, Unprocessable
from gault.compilers import CompilationError
from gault.exceptions import PipelineError
```

---

## NotFound

```python
@dataclass
class NotFound(LookupError)
```

Raised when a query returns no results and a result was required.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `model` | `type[Model]` | The Model class that was queried. |
| `filter` | `Filter` | The filter that produced no results. |

### When raised

| Method | Condition |
|---|---|
| `AsyncManager.get()` / `Manager.get()` | No document matches the filter. |
| `AsyncManager.refresh()` / `Manager.refresh()` | The document no longer exists in the database. |

### Message format

```
Instance of {ModelName} not found
```

### Example

```python
from gault import NotFound

try:
    user = await manager.get(User, User.id == "nonexistent")
except NotFound as e:
    print(e.model)   # <class 'User'>
    print(e.filter)   # the predicate or filter used
    print(e)          # "Instance of User not found"
```

---

## Forbidden

```python
@dataclass
class Forbidden(TypeError)
```

Raised when an operation is not allowed for the given model type.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `model` | `type[Model]` | The Model class that caused the error. |
| `reason` | `str` | Human-readable explanation. |

### When raised

| Method | Condition |
|---|---|
| `AsyncManager.insert()` / `Manager.insert()` | The instance is not a `Schema` subclass (plain `Model` cannot be inserted). |
| `AsyncManager.save()` / `Manager.save()` | The instance is not a `Schema` subclass. |

### Message format

```
Forbidden {ModelName} ; {reason}
```

### Example

```python
from gault import Forbidden

class ReadOnlyView(Model, collection="users"):
    name: str

try:
    await manager.insert(ReadOnlyView(name="Alice"))
except Forbidden as e:
    print(e.model)   # <class 'ReadOnlyView'>
    print(e.reason)  # "Only model allowed for insert"
    print(e)         # "Forbidden ReadOnlyView ; Only model allowed for insert"
```

---

## Unprocessable

```python
@dataclass
class Unprocessable(ValueError)
```

Raised when an operation cannot be performed because the model definition is incomplete or invalid.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `model` | `type[Model]` | The Model class. |
| `reason` | `str` | Human-readable explanation. |

### When raised

| Method | Condition |
|---|---|
| `AsyncManager.save()` / `Manager.save()` | The model has no field marked as `pk=True`. A primary key is required to construct the upsert filter. |
| `AsyncManager.refresh()` / `Manager.refresh()` | The model has no field marked as `pk=True`. A primary key is required to look up the document. |

### Message format

```
Unprocessable {ModelName} ; {reason}
```

### Example

```python
from gault import Unprocessable

class NoPK(Schema, collection="things"):
    name: str  # no pk=True field

try:
    await manager.save(NoPK(name="test"))
except Unprocessable as e:
    print(e.model)   # <class 'NoPK'>
    print(e.reason)  # "model must declare one field as pk"
    print(e)         # "Unprocessable NoPK ; model must declare one field as pk"
```

---

## CompilationError

```python
@dataclass
class CompilationError(Exception)
```

Raised when gault cannot compile an expression, query, field reference, or path. This typically indicates a type mismatch or unsupported value in the pipeline/predicate construction.

Defined in `gault.compilers`.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `message` | `str` | Description of the compilation error. |
| `target` | `Any \| None` | The object that failed to compile. |

### When raised

| Function | Condition |
|---|---|
| `compile_query()` | The value is not a `QueryPredicate`, `ExpressionOperator`, or `dict`. |
| `compile_expression()` | The value is not a recognized expression type (not a string, number, bool, None, dict, list, date, ObjectId, Binary, Timestamp, or ExpressionOperator). |
| `compile_path()` | A string value does not start with `$` (it looks like a field name instead of a path). |
| `compile_field()` | A string value starts with `$` (it looks like a path instead of a field name). |

### Message examples

```
compile query is not implemented for type <class 'SomeType'>
compile expression is not implemented for type <class 'SomeType'>
Value 'name' looks like a field
Value '$name' looks like a path
```

### Example

```python
from gault.compilers import CompilationError

try:
    Pipeline().match(42)  # invalid filter type
except CompilationError as e:
    print(e.message)  # "compile query is not implemented for type <class 'int'>"
    print(e.target)   # 42
```

---

## PipelineError

```python
class PipelineError(Exception)
```

Raised for pipeline-level errors. Defined in `gault.exceptions`.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `pipeline` | `Pipeline` | The pipeline that caused the error. |
| `reason` | `str` | Human-readable explanation. |

### Message format

```
Pipeline error ; {reason}
```

---

## Exception hierarchy

```
BaseException
  Exception
    LookupError
      NotFound
    TypeError
      Forbidden
    ValueError
      Unprocessable
    Exception
      CompilationError
      PipelineError
```

All gault exceptions inherit from standard Python exception types, so they can be caught with broad except clauses when appropriate:

```python
try:
    user = await manager.get(User, User.id == "x")
except LookupError:
    # catches NotFound and any other LookupError
    pass
```
