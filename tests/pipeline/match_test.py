from gault import Attribute, Model
from gault.expressions import Var
from gault.pipelines import Pipeline
from gault.predicates import Field


def test_query_predicates(subtests):
    # TODO: match operator
    # TODO: match query predicate

    pipeline = Pipeline()
    pipeline = pipeline.match({"attr1": True, "attr2": False})
    result = pipeline.build()
    assert result == [
        {
            "$match": {
                "attr1": True,
                "attr2": False,
            },
        },
    ]


def test_operator_predicates(subtests):
    class MyModel(Model, collection="coll"):
        id: Attribute[str]
        age: Attribute[int]
        name: Attribute[str]

    query = (
        MyModel.id.eq("foo")
        & MyModel.age.in_([1, 2, 3])
        & MyModel.name.ne(Var("other"))
    )

    pipeline = Pipeline()
    pipeline = pipeline.match(query)
    result = pipeline.build()
    assert result == [
        {
            "$match": {
                "$and": [
                    {"id": {"$eq": "foo"}},
                    {"age": {"$in": [1, 2, 3]}},
                    {"name": {"$ne": "$$other"}},
                ],
            }
        },
    ]


def test_field_predicates(subtests):
    query = (
        Field("id").eq("foo")
        & Field("age").in_(1, 2, 3)
        & Field("name").ne(Var("other"))
    )

    pipeline = Pipeline()
    pipeline = pipeline.match(query)
    result = pipeline.build()
    assert result == [
        {
            "$match": {
                "$and": [
                    {"id": {"$eq": "foo"}},
                    {"age": {"$in": [1, 2, 3]}},
                    {"name": {"$ne": "$$other"}},
                ],
            }
        },
    ]


def test_spread_predicates(subtests):
    query1 = {"attr1": True, "attr2": False}
    query2 = {"attr3": True, "attr4": False}

    pipeline = Pipeline()
    pipeline = pipeline.match(
        query1,
        query2,
    )
    result = pipeline.build()

    assert result == [
        {
            "$match": {
                "$and": [
                    {"attr1": True, "attr2": False},
                    {"attr3": True, "attr4": False},
                ]
            }
        }
    ]


def test_list_predicates(subtests):
    query1 = {"attr1": True, "attr2": False}
    query2 = {"attr3": True, "attr4": False}

    pipeline = Pipeline()
    pipeline = pipeline.match(
        [
            query1,
            query2,
        ]
    )
    result = pipeline.build()

    assert result == [
        {
            "$match": {
                "$and": [
                    {"attr1": True, "attr2": False},
                    {"attr3": True, "attr4": False},
                ]
            }
        }
    ]
