# Reference

Complete API reference for the gault MongoDB ODM library. Every public class, function, parameter, and return type is documented here.

## Sections

| Section | Description |
|---|---|
| [Schema and Model](schema-and-model.md) | `Schema`, `Model`, `Attribute`, `configure()`, `get_schema()`, `get_collection()`, `Page` |
| [Manager](manager.md) | `AsyncManager`, `Manager`, `Persistence`, `StateTracker` -- query, insert, save, refresh, paginate |
| [Pipeline](pipeline.md) | `Pipeline`, `CollectionPipeline`, `DocumentsPipeline` -- aggregation pipeline builder |
| [Expressions](expressions.md) | Aggregation expression operators: arithmetic, comparison, string, array, date, type, conditional |
| [Accumulators](accumulators.md) | Group accumulators: `Sum`, `Avg`, `Count`, `Min`, `Max`, `First`, `Last`, `Push`, `AddToSet`, and more |
| [Predicates](predicates.md) | Query predicates: `Field`, `Query`, comparison, logical, array, regex, existence, and type operators |
| [Exceptions](exceptions.md) | `NotFound`, `Forbidden`, `Unprocessable`, `CompilationError`, `PipelineError` |

## Import convention

All public symbols are available from the top-level package:

```python
from gault import (
    Schema, Model, Attribute, configure, get_schema, get_collection, Page,
    AsyncManager, Manager, Persistence, StateTracker,
    Pipeline, CollectionPipeline,
    Field, Query,
    Accumulator, Sum,
    Var,
    Forbidden, NotFound, Unprocessable,
    Mapper, get_mapper,
)
```

Expressions and accumulators beyond those re-exported at the top level are available from their respective submodules:

```python
from gault.expressions import Add, Subtract, Cond, Filter, Map
from gault.accumulators import Avg, Count, Max, Min, Push, AddToSet
from gault.predicates import And, Or, Nor, Not, Eq, Gt, In, Regex
```
