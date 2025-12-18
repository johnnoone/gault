from __future__ import annotations

from strata.models import AttributeSpec, Schema


def test_predicates(subtests, context):
    class Foo(Schema, collection="coll"):
        pass

    attr = AttributeSpec(Foo, "attr1", "alias1")
    other = "value"

    with subtests.test(".__eq__(other)"):
        predicate = attr == other
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$eq": "value"}}

    with subtests.test(".eq(other)"):
        predicate = attr.eq(other)
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$eq": "value"}}

    with subtests.test(".__ne__(other)"):
        predicate = attr != other
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$ne": "value"}}

    with subtests.test(".ne(other)"):
        predicate = attr.ne(other)
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$ne": "value"}}

    with subtests.test(".__lt__(other)"):
        predicate = attr < other
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$lt": "value"}}

    with subtests.test(".lt(other)"):
        predicate = attr.lt(other)
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$lt": "value"}}

    with subtests.test(".__le__(other)"):
        predicate = attr <= other
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$lte": "value"}}

    with subtests.test(".lte(other)"):
        predicate = attr.lte(other)
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$lte": "value"}}

    with subtests.test(".__gt__(other)"):
        predicate = attr > other
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$gt": "value"}}

    with subtests.test(".gte(other)"):
        predicate = attr.gte(other)
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$gte": "value"}}

    with subtests.test(".in_(other)"):
        predicate = attr.in_(other)
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$in": ["value"]}}

    with subtests.test(".nin(other)"):
        predicate = attr.nin(other)
        op = predicate.compile_query(context=context)
        assert op == {"alias1": {"$nin": ["value"]}}
