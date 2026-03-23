# Explanation

These articles explain the design decisions and architecture behind Gault. They are intended to deepen your understanding of *why* Gault works the way it does, rather than *how* to use it.

- [Schema vs Model](schema-vs-model.md) -- Why Gault distinguishes between persistent schemas and non-persistent models, and how the collection registry ties them together.
- [Persistence & State Tracking](persistence-and-state.md) -- How Gault tracks which instances exist in the database and which fields have changed, enabling atomic saves without manual bookkeeping.
- [Pipeline Architecture](pipeline-architecture.md) -- The immutable, step-based pipeline design that compiles Pythonic method chains into MongoDB aggregation stages.
