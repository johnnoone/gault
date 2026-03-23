from __future__ import annotations

from gault.shapes import Shape


def test_shape_compile_expression_abstract(context):
    class Concrete(Shape):
        def compile_expression(self, *, context):
            return super().compile_expression(context=context)

    result = Concrete().compile_expression(context=context)
    assert result is None
