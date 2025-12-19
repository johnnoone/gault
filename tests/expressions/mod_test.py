import pytest

from gault.expressions import Mod


def test_expression(context, subtests: pytest.Subtests):
    with subtests.test():
        op = Mod("field", "value")
        result = op.compile_expression(context=context)
        assert result == {"$mod": ["field", "value"]}

    with subtests.test():
        op = Mod("field", "$value")
        result = op.compile_expression(context=context)
        assert result == {"$mod": ["field", "$value"]}
