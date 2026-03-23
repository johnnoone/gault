from __future__ import annotations

import pytest

from gault.models import Attribute, AttributeSpec, Page, Schema, get_schema
from gault.predicates import Field


def test_attribute_set_name():
    """Line 149: Attribute.__set_name__ is called by descriptor protocol."""
    attr = Attribute()
    attr.__set_name__(object, "my_field")
    assert attr.name == "my_field"


def test_types_module_import():
    """types.py lines 1-5: ensure the module is importable at runtime."""
    import gault.types  # noqa: F401


def test_get_schema():
    class Foo(Schema, collection="test_get_schema_coll"):
        pass

    result = get_schema("test_get_schema_coll")
    assert result is Foo


def test_schema_without_collection():
    with pytest.raises(ValueError, match="collection is required"):

        class Bad(Schema, collection=None):  # type: ignore[call-arg]
            pass


def test_attribute_spec_get_db_alias():
    class Foo(Schema, collection="test_db_alias_coll"):
        pass

    attr = AttributeSpec(Foo, "name", db_alias="alias")
    assert attr.get_db_alias() == "alias"


def test_attribute_spec_hash():
    class Foo(Schema, collection="test_hash_coll"):
        pass

    attr = AttributeSpec(Foo, "name", db_alias="alias")
    assert hash(attr) == hash((Foo, "name", "alias"))


def test_attribute_spec_ge(context):
    class Foo(Schema, collection="test_ge_coll"):
        pass

    attr = AttributeSpec(Foo, "name", db_alias="alias")
    predicate = attr >= 10
    result = predicate.compile_query(context=context)
    assert result == {"alias": {"$gte": 10}}


def test_attribute_spec_field():
    sub = Field("parent").field("child")
    assert sub.name == "parent.child"


def test_page_with():
    page = Page(instances=[1, 2, 3], total=3, page=1, per_page=10)
    result = page.with_(lambda x: x * 2)
    assert result.instances == [2, 4, 6]
    assert result.total == 3


def test_page_getitem():
    page = Page(instances=["a", "b", "c"], total=3, page=1, per_page=10)
    assert page[0] == "a"
    assert page[1] == "b"


def test_page_iter():
    page = Page(instances=[1, 2, 3], total=3, page=1, per_page=10)
    assert list(page) == [1, 2, 3]


def test_page_reversed():
    page = Page(instances=[1, 2, 3], total=3, page=1, per_page=10)
    assert list(reversed(page)) == [3, 2, 1]


def test_page_contains():
    page = Page(instances=[1, 2, 3], total=3, page=1, per_page=10)
    assert 2 in page
    assert 4 not in page
