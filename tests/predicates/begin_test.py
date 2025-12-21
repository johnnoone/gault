from gault.predicates import Begin, Field
from gault.interfaces import QueryPredicate


def test_begin(context):
    query: QueryPredicate = Begin()
    result = query.compile_query(context=context)
    assert result == {}

    query = Begin() & Field("attr").eq("$other")
    result = query.compile_query(context=context)
    assert result == {
        "$and": [
            {
                "attr": {
                    "$eq": "$other",
                },
            }
        ]
    }
