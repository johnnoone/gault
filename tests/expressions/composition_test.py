from gault.expressions import Var


def test_and_composition(context):
    expression = Var("foo").eq("bar") & Var("baz").ne("quz")

    assert expression.compile_expression(context=context) == {
        "$and": [
            {"$eq": ["$$foo", "bar"]},
            {"$ne": ["$$baz", "quz"]},
        ]
    }


def test_or_composition(context):
    expression = Var("foo").eq("bar") | Var("baz").ne("quz")

    assert expression.compile_expression(context=context) == {
        "$or": [
            {"$eq": ["$$foo", "bar"]},
            {"$ne": ["$$baz", "quz"]},
        ]
    }


def test_not_composition(context):
    expression = ~(Var("foo").eq("bar") | Var("baz").ne("quz"))

    print(expression.compile_expression(context=context))
    assert expression.compile_expression(context=context) == {
        "$not": [
            {
                "$or": [
                    {"$eq": ["$$foo", "bar"]},
                    {"$ne": ["$$baz", "quz"]},
                ]
            }
        ]
    }


def test_not_not_composition(context):
    expression = ~(~(Var("foo").eq("bar") | Var("baz").ne("quz")))

    print(expression.compile_expression(context=context))
    assert expression.compile_expression(context=context) == {
        "$or": [
            {"$eq": ["$$foo", "bar"]},
            {"$ne": ["$$baz", "quz"]},
        ]
    }
