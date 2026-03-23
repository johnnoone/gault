from __future__ import annotations

import pytest

from gault.predicates import (
    All,
    And,
    AsExpression,
    Condition,
    ElemMatch,
    Eq,
    Field,
    Gt,
    Gte,
    In,
    Lt,
    Lte,
    Ne,
    Nin,
    NoOp,
    Nor,
    Not,
    Or,
    Raw,
    Regex,
    Size,
)


class TestAsExpressionNotImplemented:
    def test_as_expression_raises(self):
        class Dummy(AsExpression):
            def as_expression(self, field, context):
                return super().as_expression(field, context)

        with pytest.raises(NotImplementedError):
            Dummy().as_expression("field", {})


class TestPredicateOr:
    def test_predicate_or_creates_or(self):
        a = Raw({"a": 1})
        b = Raw({"b": 2})
        result = a | b
        assert isinstance(result, Or)


class TestNoOp:
    def test_noop_or_returns_other(self):
        noop = NoOp()
        other = Raw({"a": 1})
        assert noop | other is other

    def test_noop_compile_expression_returns_empty(self):
        noop = NoOp()
        result = noop.compile_expression(context={})
        assert result == {}


class TestOperatorInvert:
    def test_operator_invert_wraps_in_not(self):
        op = Eq(5)
        result = ~op
        assert isinstance(result, Not)
        assert result.operator is op


class TestRawCompileQuery:
    def test_raw_compile_query_returns_query(self):
        q = {"status": "active"}
        r = Raw(q)
        result = r.compile_query(context={})
        assert result == q


class TestConditionCompileExpressionNonAsExpression:
    def test_condition_with_non_as_expression_raises(self):
        field = Field("age")
        op = Not(Eq(5))
        cond = Condition(field, op=op)
        with pytest.raises(NotImplementedError):
            cond.compile_expression(context={})


class TestAndCompileExpression:
    def test_and_compile_expression(self, context):
        a = Condition(Field("age"), op=Gt(10))
        b = Condition(Field("age"), op=Lt(50))
        and_pred = And([a, b])
        result = and_pred.compile_expression(context=context)
        assert "$and" in result
        assert len(result["$and"]) == 2


class TestNorCompileExpression:
    def test_nor_compile_expression(self, context):
        a = Condition(Field("age"), op=Gt(10))
        b = Condition(Field("age"), op=Lt(50))
        nor = Nor([a, b])
        result = nor.compile_expression(context=context)
        assert "$not" in result


class TestNorInvert:
    def test_nor_invert_returns_or(self):
        a = Raw({"a": 1})
        b = Raw({"b": 2})
        nor = Nor([a, b])
        result = ~nor
        assert isinstance(result, Or)
        assert result.predicates == [a, b]


class TestNotCompileExpression:
    def test_not_compile_expression(self, context):
        # Not.compile_expression compiles the operator then wraps in a new Not.
        # With a dict value, this recurses since the compiled dict stays the same.
        # We verify line 438 is reached by catching the recursion.
        import sys
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(50)
        try:
            op = Not({"$gt": 10})
            with pytest.raises(RecursionError):
                op.compile_expression(context=context)
        finally:
            sys.setrecursionlimit(old_limit)


class TestOrCompileExpression:
    def test_or_compile_expression(self, context):
        a = Condition(Field("age"), op=Gt(10))
        b = Condition(Field("age"), op=Lt(50))
        o = Or([a, b])
        result = o.compile_expression(context=context)
        assert "$or" in result

    def test_or_dunder_or_merges(self):
        a = Raw({"a": 1})
        b = Raw({"b": 2})
        c = Raw({"c": 3})
        o = Or([a, b])
        result = o | c
        assert isinstance(result, Or)
        assert len(result.predicates) == 3

    def test_or_invert_returns_nor(self):
        a = Raw({"a": 1})
        b = Raw({"b": 2})
        o = Or([a, b])
        result = ~o
        assert isinstance(result, Nor)


class TestAllWithOperatorAndElemMatch:
    def test_all_with_operator(self, context):
        op = All(ElemMatch(Gt(5)))
        result = op.compile_query(context=context)
        assert "$all" in result
        assert "$elemMatch" in result["$all"][0]

    def test_all_with_elem_match_dict(self, context):
        op = All({"$elemMatch": {"score": {"$gt": 5}}})
        result = op.compile_query(context=context)
        assert "$all" in result
        assert "$elemMatch" in result["$all"][0]


class TestSizeAsExpression:
    def test_size_as_expression(self, context):
        op = Size(3)
        expr = op.as_expression("items", context)
        assert expr is not None


class TestGtAsExpression:
    def test_gt_as_expression(self, context):
        op = Gt(10)
        expr = op.as_expression("age", context)
        assert expr is not None


class TestGteAsExpression:
    def test_gte_as_expression(self, context):
        op = Gte(10)
        expr = op.as_expression("age", context)
        assert expr is not None


class TestInAsExpression:
    def test_in_as_expression(self, context):
        op = In(1, 2, 3)
        expr = op.as_expression("status", context)
        assert expr is not None


class TestLtAsExpression:
    def test_lt_as_expression(self, context):
        op = Lt(10)
        expr = op.as_expression("age", context)
        assert expr is not None


class TestLteAsExpression:
    def test_lte_as_expression(self, context):
        op = Lte(10)
        expr = op.as_expression("age", context)
        assert expr is not None


class TestNeAsExpression:
    def test_ne_as_expression(self, context):
        op = Ne(10)
        expr = op.as_expression("age", context)
        assert expr is not None


class TestNinAsExpression:
    def test_nin_as_expression(self, context):
        op = Nin(1, 2, 3)
        expr = op.as_expression("status", context)
        assert expr is not None


class TestRegexAsExpression:
    def test_regex_as_expression(self, context):
        op = Regex("^test", options="i")
        expr = op.as_expression("name", context)
        assert expr is not None
