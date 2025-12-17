from strata.expressions import Var
import pytest


@pytest.fixture(name="context")
def get_context():
    return {}


def test_compile(context):
    var = Var("my_var")
    assert var.compile_field(context=context) == "my_var"
    assert var.compile_expression(context=context) == "$$my_var"


def test_sort(context):
    var = Var("my_var")
    assert var.asc() == (var, 1)
    assert var.desc() == (var, -1)
    assert var.by_score("my_name") == (var, {"$meta": "my_name"})
