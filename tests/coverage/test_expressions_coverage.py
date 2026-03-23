from __future__ import annotations

import pytest

from gault.expressions import (
    Add,
    And,
    Avg,
    BitAnd,
    BitOr,
    BitXor,
    Concat,
    ConcatArrays,
    Filter,
    IfNull,
    IndexOfArray,
    IndexOfBytes,
    IndexOfCP,
    Map,
    Max,
    Median,
    Min,
    Not,
    Or,
    Percentile,
    Raw,
    SetEquals,
    SetIntersection,
    SetUnion,
    StdDevPop,
    StdDevSamp,
    Subtract,
    Sum,
    Var,
)


class TestAddValidation:
    def test_add_with_less_than_2_inputs_raises(self):
        with pytest.raises(ValueError, match="Multiple values is required"):
            Add(1)

    def test_add_with_empty_raises(self):
        with pytest.raises(ValueError, match="Multiple values is required"):
            Add()


class TestAndValidation:
    def test_and_with_no_inputs_raises(self):
        with pytest.raises(ValueError, match="Multiple inputs is required"):
            And()

    def test_and_dunder_and_merges_inputs(self):
        a = And(1, 2)
        result = a & Raw(3)
        assert isinstance(result, And)
        assert result.inputs == [1, 2, Raw(3)]


class TestAvgCompileMultiInput:
    def test_avg_compile_with_list(self, context):
        op = Avg(input=[1, 2, 3])
        result = op.compile_expression(context=context)
        assert result == {"$avg": [1, 2, 3]}


class TestBitAndValidation:
    def test_bitand_with_less_than_2_raises(self):
        with pytest.raises(ValueError, match="Multiple values required"):
            BitAnd(1)

    def test_bitand_with_empty_raises(self):
        with pytest.raises(ValueError, match="Multiple values required"):
            BitAnd()


class TestBitOrValidation:
    def test_bitor_with_less_than_2_raises(self):
        with pytest.raises(ValueError, match="Multiple values required"):
            BitOr(1)

    def test_bitor_with_empty_raises(self):
        with pytest.raises(ValueError, match="Multiple values required"):
            BitOr()


class TestBitXorValidation:
    def test_bitxor_with_empty_raises(self):
        with pytest.raises(ValueError, match="Values is required"):
            BitXor()


class TestConcatValidation:
    def test_concat_with_empty_raises(self):
        with pytest.raises(ValueError, match="Values is required"):
            Concat()


class TestConcatArraysValidation:
    def test_concatarrays_with_empty_raises(self):
        with pytest.raises(ValueError, match="Values is required"):
            ConcatArrays()


class TestFilterVarAsString:
    def test_filter_with_string_var(self, context):
        op = Filter(input="$items", cond=True, var="item")
        result = op.compile_expression(context=context)
        assert result["$filter"]["as"] == "item"


class TestIfNullValidation:
    def test_ifnull_with_no_inputs_raises(self):
        with pytest.raises(ValueError, match="Multiple inputs is required"):
            IfNull()


class TestIndexOfArrayEndNoStart:
    def test_end_but_no_start_defaults_start_to_0(self):
        op = IndexOfArray(input="$arr", search="x", end=10)
        assert op.start == 0


class TestIndexOfBytesEndNoStart:
    def test_end_but_no_start_defaults_start_to_0(self):
        op = IndexOfBytes(input="$str", search="x", end=10)
        assert op.start == 0


class TestIndexOfCPEndNoStart:
    def test_end_but_no_start_defaults_start_to_0(self):
        op = IndexOfCP(input="$str", search="x", end=10)
        assert op.start == 0


class TestMapVarAsVar:
    def test_map_with_var_instance(self, context):
        v = Var("elem")
        op = Map(input="$items", into="$$elem", var=v)
        result = op.compile_expression(context=context)
        assert result["$map"]["as"] == "elem"

    def test_map_with_callable_into(self, context):
        op = Map(input="$items", into=lambda var, ctx: "$$var_result", var="x")
        result = op.compile_expression(context=context)
        assert result["$map"]["in"] == "$$var_result"


class TestMedianCompileWithList:
    def test_median_compile_with_list_input(self, context):
        # Median only has compile (not compile_expression), so we call compile directly
        # We cannot instantiate directly because compile_expression is abstract,
        # so we subclass to provide the abstract method.
        class ConcreteMedian(Median):
            def compile_expression(self, *, context):
                return self.compile(context=context)

        op = ConcreteMedian(input=[1, 2, 3])
        result = op.compile(context=context)
        assert result == {
            "$median": {
                "input": [1, 2, 3],
                "method": "approximate",
            },
        }


class TestNotInvert:
    def test_not_invert_with_raw_returns_input(self):
        raw = Raw(42)
        op = Not(raw)
        result = ~op
        assert result is raw

    def test_not_invert_with_non_raw_returns_raw(self):
        op = Not(42)
        result = ~op
        assert isinstance(result, Raw)
        assert result.input == 42


class TestOrValidation:
    def test_or_with_no_inputs_raises(self):
        with pytest.raises(ValueError, match="Values is required"):
            Or()

    def test_or_dunder_or_merges_inputs(self):
        a = Or(1, 2)
        result = a | Raw(3)
        assert isinstance(result, Or)
        assert result.inputs == [1, 2, Raw(3)]


class TestPercentileCompile:
    def test_percentile_compile_expression(self, context):
        op = Percentile(input="$score", p=[0.5, 0.9])
        result = op.compile_expression(context=context)
        assert result == {
            "$percentile": {
                "input": "$score",
                "p": [0.5, 0.9],
                "method": "approximate",
            },
        }


class TestSetEqualsValidation:
    def test_setequals_with_less_than_2_raises(self):
        with pytest.raises(ValueError, match="Requires at least 2 sets"):
            SetEquals("only_one")


class TestSetIntersectionValidation:
    def test_setintersection_with_less_than_2_raises(self):
        with pytest.raises(ValueError, match="Requires at least 2 sets"):
            SetIntersection("only_one")


class TestSetUnionValidation:
    def test_setunion_with_less_than_2_raises(self):
        with pytest.raises(ValueError, match="Requires at least 2 sets"):
            SetUnion("only_one")


class TestStdDevPopCompile:
    def test_stddevpop_compile_expression(self, context):
        op = StdDevPop(input=[1, 2, 3])
        result = op.compile_expression(context=context)
        assert result == {"$stdDevPop": [1, 2, 3]}


class TestStdDevSampCompile:
    def test_stddevsamp_compile_expression(self, context):
        op = StdDevSamp(input=[1, 2, 3])
        result = op.compile_expression(context=context)
        assert result == {"$stdDevSamp": [1, 2, 3]}


class TestSumCompile:
    def test_sum_compile_expression(self, context):
        op = Sum(input=[1, 2, 3])
        result = op.compile_expression(context=context)
        assert result == {"$sum": [1, 2, 3]}


class TestExpressionsInterfaceAvgMulti:
    def test_avg_with_multiple_inputs(self):
        v = Var("x")
        result = v.avg(1, 2)
        assert isinstance(result, Avg)
        assert isinstance(result.input, list)
        assert len(result.input) == 3


class TestExpressionsInterfaceMaxMulti:
    def test_max_with_multiple_inputs(self):
        v = Var("x")
        result = v.max(1, 2)
        assert isinstance(result, Max)
        assert isinstance(result.input, list)
        assert len(result.input) == 3


class TestExpressionsInterfaceMinMulti:
    def test_min_with_multiple_inputs(self):
        v = Var("x")
        result = v.min(1, 2)
        assert isinstance(result, Min)
        assert isinstance(result.input, list)
        assert len(result.input) == 3


class TestExpressionsInterfaceGetRef:
    def test_get_ref_abstract(self):
        """Line 2731: ExpressionsInterface.get_ref body (pass)."""
        from gault.expressions import ExpressionsInterface

        class Concrete(ExpressionsInterface):
            def get_ref(self):
                return super().get_ref()

        result = Concrete().get_ref()
        assert result is None


class TestExpressionsInterfaceNoArgs:
    def test_avg_no_args(self):
        v = Var("x")
        result = v.avg()
        assert isinstance(result, Avg)

    def test_max_no_args(self):
        v = Var("x")
        result = v.max()
        assert isinstance(result, Max)

    def test_min_no_args(self):
        v = Var("x")
        result = v.min()
        assert isinstance(result, Min)


class TestExpressionsInterfaceSubtract:
    def test_subtract(self):
        v = Var("x")
        result = v.subtract(5)
        assert isinstance(result, Subtract)
