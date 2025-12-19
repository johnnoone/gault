from gault.mappers import Corres, Mapper
from gault.models import Attribute, Schema, configure


class MyModel(Schema, collection="my-collection"):
    id: Attribute[int] = configure(pk=True)
    name: Attribute[str] = configure(db_alias="db_name")
    age: Attribute[int]


def test_mapper():
    mapper = Mapper(MyModel)
    assert mapper.db_fields == {"id", "db_name", "age"}
    assert mapper.field_mapping == [
        Corres(model_field="id", db_field="id", pk=True),
        Corres(model_field="name", db_field="db_name", pk=False),
        Corres(model_field="age", db_field="age", pk=False),
    ]
