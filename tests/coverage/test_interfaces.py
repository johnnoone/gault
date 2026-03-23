from __future__ import annotations

import pytest

from gault.interfaces import AsRef, AttributeBase, ExpressionOperator, QueryPredicate
from gault.models import Schema


def test_attribute_base_repr_without_db_alias():
    class Foo(Schema, collection="test_repr_no_alias"):
        pass

    attr = AttributeBase(Foo, "name")
    result = repr(attr)
    assert result == "AttributeBase(Foo, 'name')"


def test_attribute_base_repr_with_db_alias():
    class Foo(Schema, collection="test_repr_alias"):
        pass

    attr = AttributeBase(Foo, "name", db_alias="alias")
    result = repr(attr)
    assert result == "AttributeBase(Foo, 'name', db_alias='alias')"


def test_query_predicate_compile_query_not_implemented(context):
    class Concrete(QueryPredicate):
        def compile_query(self, *, context):
            return super().compile_query(context=context)

    with pytest.raises(NotImplementedError):
        Concrete().compile_query(context=context)


def test_expression_operator_compile_expression_not_implemented(context):
    class Concrete(ExpressionOperator):
        def compile_expression(self, *, context):
            return super().compile_expression(context=context)

    with pytest.raises(NotImplementedError):
        Concrete().compile_expression(context=context)


def test_as_ref_compile_field_not_implemented(context):
    class Concrete(AsRef):
        def compile_field(self, *, context):
            return super().compile_field(context=context)

        def compile_expression(self, *, context):
            return ""

    with pytest.raises(NotImplementedError):
        Concrete().compile_field(context=context)


def test_as_ref_compile_expression_not_implemented(context):
    class Concrete(AsRef):
        def compile_field(self, *, context):
            return ""

        def compile_expression(self, *, context):
            return super().compile_expression(context=context)

    with pytest.raises(NotImplementedError):
        Concrete().compile_expression(context=context)
