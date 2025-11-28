from __future__ import annotations
from mongo_odm import (
    Gt,
    Gte,
    In,
    Lt,
    Lte,
    Model,
    Nin,
    Attribute,
    Eq,
    Path,
    Ne,
    And,
    Or,
    Not,
)


def test_operation_eq(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert Eq(attr1, attr2).compile() == {"alias1": {"$eq": "$alias2"}}

    with subtests.test():
        assert Eq("my_key", "value").compile() == {"my_key": {"$eq": "value"}}

    with subtests.test():
        assert Eq("my_key", Path("my.path")).compile() == {
            "my_key": {"$eq": "$my.path"}
        }

    with subtests.test():
        assert Eq(Path("my.path"), "value").compile() == {"my.path": {"$eq": "value"}}


def test_operation_ne(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert Ne(attr1, attr2).compile() == {"alias1": {"$ne": "$alias2"}}

    with subtests.test():
        assert Ne("my_key", "value").compile() == {"my_key": {"$ne": "value"}}

    with subtests.test():
        assert Ne("my_key", Path("my.path")).compile() == {
            "my_key": {"$ne": "$my.path"}
        }

    with subtests.test():
        assert Ne(Path("my.path"), "value").compile() == {"my.path": {"$ne": "value"}}


def test_operation_lt(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert Lt(attr1, attr2).compile() == {"alias1": {"$lt": "$alias2"}}

    with subtests.test():
        assert Lt("my_key", "value").compile() == {"my_key": {"$lt": "value"}}

    with subtests.test():
        assert Lt("my_key", Path("my.path")).compile() == {
            "my_key": {"$lt": "$my.path"}
        }

    with subtests.test():
        assert Lt(Path("my.path"), "value").compile() == {"my.path": {"$lt": "value"}}


def test_operation_lte(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert Lte(attr1, attr2).compile() == {"alias1": {"$lte": "$alias2"}}

    with subtests.test():
        assert Lte("my_key", "value").compile() == {"my_key": {"$lte": "value"}}

    with subtests.test():
        assert Lte("my_key", Path("my.path")).compile() == {
            "my_key": {"$lte": "$my.path"}
        }

    with subtests.test():
        assert Lte(Path("my.path"), "value").compile() == {"my.path": {"$lte": "value"}}


def test_operation_gt(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert Gt(attr1, attr2).compile() == {"alias1": {"$gt": "$alias2"}}

    with subtests.test():
        assert Gt("my_key", "value").compile() == {"my_key": {"$gt": "value"}}

    with subtests.test():
        assert Gt("my_key", Path("my.path")).compile() == {
            "my_key": {"$gt": "$my.path"}
        }

    with subtests.test():
        assert Gt(Path("my.path"), "value").compile() == {"my.path": {"$gt": "value"}}


def test_operation_gte(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert Gte(attr1, attr2).compile() == {"alias1": {"$gte": "$alias2"}}

    with subtests.test():
        assert Gte("my_key", "value").compile() == {"my_key": {"$gte": "value"}}

    with subtests.test():
        assert Gte("my_key", Path("my.path")).compile() == {
            "my_key": {"$gte": "$my.path"}
        }

    with subtests.test():
        assert Gte(Path("my.path"), "value").compile() == {"my.path": {"$gte": "value"}}


def test_operation_in(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert In(attr1, attr2).compile() == {"alias1": {"$in": "$alias2"}}

    with subtests.test():
        assert In("my_key", "value").compile() == {"my_key": {"$in": "value"}}

    with subtests.test():
        assert In("my_key", Path("my.path")).compile() == {
            "my_key": {"$in": "$my.path"}
        }

    with subtests.test():
        assert In(Path("my.path"), "value").compile() == {"my.path": {"$in": "value"}}


def test_operation_nin(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr1 = Attribute(Foo, "attr1", "alias1")
    attr2 = Attribute(Foo, "attr2", "alias2")

    with subtests.test():
        assert Nin(attr1, attr2).compile() == {"alias1": {"$nin": "$alias2"}}

    with subtests.test():
        assert Nin("my_key", "value").compile() == {"my_key": {"$nin": "value"}}

    with subtests.test():
        assert Nin("my_key", Path("my.path")).compile() == {
            "my_key": {"$nin": "$my.path"}
        }

    with subtests.test():
        assert Nin(Path("my.path"), "value").compile() == {"my.path": {"$nin": "value"}}


def test_operation_and(subtests):
    op1 = Eq("attr1", "val1")
    op2 = Eq("attr2", "val2")
    op3 = Eq("attr3", "val3")
    op4 = Eq("attr4", "val4")

    comp1 = op1.compile()
    comp2 = op2.compile()

    op = op1 & op2
    assert op == And([op1, op2])
    assert op.compile() == {"$and": [comp1, comp2]}

    op = op1 & op2 & op3
    assert op == And([op1, op2, op3])

    op = (op1 & op2) & (op3 & op4)
    assert op == And([op1, op2, op3, op4])


def test_operation_or(subtests):
    op1 = Eq("attr1", "val1")
    op2 = Eq("attr2", "val2")
    op3 = Eq("attr3", "val3")
    op4 = Eq("attr4", "val4")

    comp1 = op1.compile()
    comp2 = op2.compile()

    op = op1 | op2
    assert op == Or([op1, op2])
    assert op.compile() == {"$or": [comp1, comp2]}

    op = op1 | op2 | op3
    assert op == Or([op1, op2, op3])

    op = (op1 | op2) | (op3 | op4)
    assert op == Or([op1, op2, op3, op4])


def test_operation_not(subtests):
    op = ~Eq("attr1", "val1")
    assert op == Not(Eq("attr1", "val1"))
    assert op.compile() == {"$not": {"attr1": {"$eq": "val1"}}}

    op = ~Not(Eq("attr1", "val1"))
    assert op == Eq("attr1", "val1")
    assert op.compile() == {"attr1": {"$eq": "val1"}}


def test_attribute_operators(subtests):
    class Foo(Model, collection="coll"):
        pass

    attr = Attribute(Foo, "attr1", "alias1")
    other = "value"

    with subtests.test(".__eq__(other)"):
        op = attr == other
        assert op == Eq(attr, other)

    with subtests.test(".eq(other)"):
        op = attr.eq(other)
        assert op == Eq(attr, other)

    with subtests.test(".__ne__(other)"):
        op = attr != other
        assert op == Ne(attr, other)

    with subtests.test(".eq(other)"):
        op = attr.ne(other)
        assert op == Ne(attr, other)

    with subtests.test(".__lt__(other)"):
        op = attr < other
        assert op == Lt(attr, other)

    with subtests.test(".lt(other)"):
        op = attr.lt(other)
        assert op == Lt(attr, other)

    with subtests.test(".__le__(other)"):
        op = attr <= other
        assert op == Lte(attr, other)

    with subtests.test(".lte(other)"):
        op = attr.lte(other)
        assert op == Lte(attr, other)

    with subtests.test(".__gt__(other)"):
        op = attr > other
        assert op == Gt(attr, other)

    with subtests.test(".gte(other)"):
        op = attr.gte(other)
        assert op == Gte(attr, other)

    with subtests.test(".in_(other)"):
        op = attr.in_(other)
        assert op == In(attr, other)

    with subtests.test(".nin_(other)"):
        op = attr.nin(other)
        assert op == Nin(attr, other)
