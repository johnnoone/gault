from gault.shapes import Coordinates
import pytest
from gault.compilers import compile_query
from gault.interfaces import Aliased, ExpressionOperator
from gault.predicates import Eq, Field, Gte


@pytest.fixture(name="field")
def get_field():
    return Field("my_field")


def test_all(field, context):
    predicate = field.all(1, 2, 3)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$all": [1, 2, 3],
        },
    }


def test_elem_match(field, context):
    predicate = field.elem_match(Eq(1))
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$elemMatch": {"$eq": 1},
        },
    }


def test_size(field, context):
    predicate = field.size(1)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$size": 1,
        },
    }


def test_bits_all_clear(field, context):
    predicate = field.bits_all_clear([1, 2, 3])
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$bitsAllClear": [1, 2, 3],
        }
    }


def test_bits_any_clear(field, context):
    predicate = field.bits_any_clear([1, 2, 3])
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$bitsAnyClear": [1, 2, 3],
        }
    }


def test_bits_all_set(field, context):
    predicate = field.bits_all_set([1, 2, 3])
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$bitsAllSet": [1, 2, 3],
        }
    }


def test_bits_any_set(field, context):
    predicate = field.bits_any_set([1, 2, 3])
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$bitsAnySet": [1, 2, 3],
        }
    }


def test_eq(field, context):
    predicate = field.eq(1)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$eq": 1,
        }
    }


def test_gt(field, context):
    predicate = field.gt(1)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$gt": 1,
        }
    }


def test_gte(field, context):
    predicate = field.gte(1)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$gte": 1,
        }
    }


def test_in(field, context):
    predicate = field.in_(1, 2, 3)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$in": [1, 2, 3],
        }
    }


def test_lt(field, context):
    predicate = field.lt(1)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$lt": 1,
        }
    }


def test_lte(field, context):
    predicate = field.lte(1)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$lte": 1,
        }
    }


def test_ne(field, context):
    predicate = field.ne([1, 2, 3])
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$ne": [1, 2, 3],
        }
    }


def test_nin(field, context):
    predicate = field.nin(1, 2, 3)
    result = compile_query(predicate, context=context)
    assert result == {"my_field": {"$nin": [1, 2, 3]}}


def test_exists(field, context):
    predicate = field.exists(False)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$exists": False,
        }
    }


def test_type(field, context):
    predicate = field.type(1, 2, 3)
    result = compile_query(predicate, context=context)
    assert result == {"my_field": {"$type": [1, 2, 3]}}


def test_geo_intersects(field, context):
    predicate = field.geo_intersects({"$box": [[1, 2], [3, 4]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$geoIntersects": {
                "$box": [[1, 2], [3, 4]],
            }
        }
    }


def test_geo_within(field, context):
    predicate = field.geo_within({"$box": [[1, 2], [3, 4]]})
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$geoWithin": {"$box": [[1, 2], [3, 4]]},
        }
    }


def test_near(field, context):
    predicate = field.near(Coordinates(1, 2), max_distance=10)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [1, 2],
                },
                "$maxDistance": 10,
            }
        }
    }


def test_near_sphere(field, context):
    predicate = field.near_sphere(Coordinates(1, 2), max_distance=10)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [1, 2],
                },
                "$maxDistance": 10,
            }
        }
    }


def test_mod(field, context):
    predicate = field.mod(1, 2)
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$mod": [1, 2],
        }
    }


def test_regex(field, context):
    predicate = field.regex("pattern", options="xi")
    result = compile_query(predicate, context=context)
    assert result == {
        "my_field": {
            "$options": "xi",
            "$regex": "pattern",
        }
    }


def test_desc(field, context):
    result = field.desc()
    assert result == (field, -1)


def test_asc(field, context):
    result = field.asc()
    assert result == (field, 1)


def test_by_score(field, context):
    result = field.by_score("new")
    assert result == (field, {"$meta": "new"})


def test_tmp(context):
    result = Field.tmp()
    assert isinstance(result, Field)


def test_field(field, context):
    result = Field("foo").field("bar")
    assert result.compile_field(context=context) == "foo.bar"
    assert result.compile_expression(context=context) == "$foo.bar"


def test_not_gte(field, context, subtests):
    with subtests.test("fuild interface"):
        predicate = field.not_.gte(1)
        result = compile_query(predicate, context=context)
        assert result == {
            "my_field": {
                "$not": {"$gte": 1},
            }
        }

    with subtests.test("call interface"):
        predicate = field.not_(Gte(1))
        result = compile_query(predicate, context=context)
        assert result == {
            "my_field": {
                "$not": {"$gte": 1},
            }
        }


def test_keep(field: Field):
    struct = field.keep()
    assert struct == Aliased(field, True)


def test_keep_alias(field: Field):
    struct = field.keep(alias="other")
    assert struct == Aliased("other", field)


def test_remove(field: Field):
    struct = field.remove()
    assert struct == Aliased(field, "$$REMOVE")


def test_expr(field: Field, context):
    expr = field.expr.gt(42)
    assert isinstance(expr, ExpressionOperator)

    result = compile_query(expr, context=context)
    assert result == {
        "$expr": {"$gt": ["$my_field", 42]},
    }
