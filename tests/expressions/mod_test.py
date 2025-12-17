import pytest
from strata.compilers import CompilationError
from strata.expressions import Mod, compile_expression, compile_query


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Mod("field", "value")
        result = compile_expression(op, context=context)
        assert result == {"$mod": ["field", "value"]}

    with subtests.test():
        op = Mod("field", "$value")
        result = compile_expression(op, context=context)
        assert result == {"$mod": ["field", "$value"]}


def test_query(context, subtests: pytest.Subtests):
    op = Mod("field", "value")
    with pytest.raises(CompilationError) as exc_info:
        compile_query(op, context=context)
    assert exc_info.value.target is op
