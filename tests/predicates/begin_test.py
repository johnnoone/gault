from gault.predicates import Begin, Field


def test_begin(context):
    query = Begin()
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
