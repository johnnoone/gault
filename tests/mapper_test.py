from mongo_odm import Model, Mapper, Field, configure, Corres


class MyModel(Model, collection="my-collection"):
    id: Field[int] = configure(pk=True)
    name: Field[str] = configure(db_alias="db_name")
    age: Field[int]


def test_mapper():
    mapper = Mapper(MyModel)
    assert mapper.db_fields == {"id", "db_name", "age"}
    assert mapper.field_mapping == [
        Corres(model_field="id", db_field="id", pk=True),
        Corres(model_field="name", db_field="db_name", pk=False),
        Corres(model_field="age", db_field="age", pk=False),
    ]
