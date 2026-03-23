from __future__ import annotations

import pytest

from gault.compilers import (
    CompilationError,
    compile_expression,
    compile_field,
    compile_path,
    compile_query,
)


def test_compile_query_unsupported_type(context):
    with pytest.raises(CompilationError, match="compile query is not implemented"):
        compile_query(42, context=context)


def test_compilation_error_init():
    err = CompilationError("some message", target="target")
    assert str(err) == "some message"
    assert err.message == "some message"
    assert err.target == "target"


def test_compile_expression_unsupported_type(context):
    class Unsupported:
        pass

    with pytest.raises(CompilationError, match="compile expression is not implemented"):
        compile_expression(Unsupported(), context=context)


def test_compile_path_string_not_starting_with_dollar(context):
    with pytest.raises(CompilationError, match="looks like a field"):
        compile_path("field_name", context=context)


def test_compile_path_unsupported_type(context):
    with pytest.raises(CompilationError, match="compile path is not implemented"):
        compile_path(42, context=context)


def test_compile_field_string_starting_with_dollar(context):
    with pytest.raises(CompilationError, match="looks like a path"):
        compile_field("$path", context=context)


def test_compile_field_unsupported_type(context):
    with pytest.raises(CompilationError, match="compile field is not implemented"):
        compile_field(42, context=context)
