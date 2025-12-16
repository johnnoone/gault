from strata.compilers import compile_query
from strata.predicates import GeoWithin


def test_compile(context):
    predicate = GeoWithin({"$box": [[0, 0], [1, 1]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "$geoWithin": {
            "$box": [
                [0, 0],
                [1, 1],
            ]
        }
    }
