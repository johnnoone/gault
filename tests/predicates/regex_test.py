from strata.compilers import compile_query
from strata.predicates import Regex


def test_compile(context):
    predicate = Regex("some-pattern", "ix")
    result = compile_query(predicate, context=context)
    assert result == {
        "$regex": "some-pattern",
        "$options": "ix",
    }
