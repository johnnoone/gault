from gault.predicates import Query, Field
from gault.interfaces import QueryPredicate


def test_begin(context):
    query: QueryPredicate = Query()
    result = query.compile_query(context=context)
    assert result == {}

    query = Query()
    query &= Field("attr").eq("$other")
    result = query.compile_query(context=context)
    assert result == {
        "attr": {
            "$eq": "$other",
        },
    }
