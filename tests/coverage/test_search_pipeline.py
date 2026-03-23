from __future__ import annotations

from gault.pipelines import Pipeline


def test_search_basic():
    pipeline = Pipeline().search(
        index="default",
        text={"query": "mongodb", "path": "title"},
    )
    stages = pipeline.build()
    assert stages == [
        {
            "$search": {
                "index": "default",
                "text": {"query": "mongodb", "path": "title"},
            }
        }
    ]


def test_search_compound():
    pipeline = Pipeline().search(
        index="default",
        compound={
            "must": [{"text": {"query": "database", "path": "title"}}],
            "filter": [{"range": {"path": "year", "gte": 2020}}],
        },
    )
    stages = pipeline.build()
    assert stages[0]["$search"]["compound"]["must"][0]["text"]["query"] == "database"


def test_search_with_other_stages():
    pipeline = (
        Pipeline()
        .search(index="default", text={"query": "mongo", "path": "title"})
        .take(10)
    )
    stages = pipeline.build()
    assert len(stages) == 2
    assert "$search" in stages[0]
    assert "$limit" in stages[1]


def test_search_meta():
    pipeline = Pipeline().search_meta(
        index="default",
        facet={
            "facets": {"categories": {"type": "string", "path": "category"}},
            "operator": {"text": {"query": "test", "path": "title"}},
        },
    )
    stages = pipeline.build()
    assert stages == [
        {
            "$searchMeta": {
                "index": "default",
                "facet": {
                    "facets": {"categories": {"type": "string", "path": "category"}},
                    "operator": {"text": {"query": "test", "path": "title"}},
                },
            }
        }
    ]


def test_vector_search():
    pipeline = Pipeline().vector_search(
        index="vector_index",
        path="embedding",
        query_vector=[0.1, 0.2, 0.3],
        num_candidates=100,
        limit=10,
    )
    stages = pipeline.build()
    assert stages == [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": [0.1, 0.2, 0.3],
                "numCandidates": 100,
                "limit": 10,
            }
        }
    ]


def test_vector_search_with_filter():
    pipeline = Pipeline().vector_search(
        index="vector_index",
        path="embedding",
        query_vector=[0.1, 0.2, 0.3],
        num_candidates=50,
        limit=5,
        filter={"category": "science"},
    )
    stages = pipeline.build()
    assert stages[0]["$vectorSearch"]["filter"] == {"category": "science"}


def test_vector_search_then_project():
    pipeline = (
        Pipeline()
        .vector_search(
            index="idx",
            path="embedding",
            query_vector=[1.0, 2.0],
            num_candidates=10,
            limit=5,
        )
        .raw({"$project": {"title": 1, "score": {"$meta": "vectorSearchScore"}}})
    )
    stages = pipeline.build()
    assert len(stages) == 2
    assert "$vectorSearch" in stages[0]
    assert "$project" in stages[1]
