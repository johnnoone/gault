from pymongo.asynchronous.database import AsyncDatabase
import pytest
from mongo_odm import AsyncManager, Field, Model, configure, to_list, NotFound


class Person(Model, collection="my-collection"):
    id: Field[int]
    name: Field[str]
    age: Field[int] = configure(db_alias="person_age")


@pytest.fixture(name="people")
async def get_people(database: AsyncDatabase):
    await database.get_collection("my-collection").insert_many(
        [
            {"id": 1, "name": "name1", "person_age": 22},
            {"id": 2, "name": "name2", "person_age": 22},
            {"id": 123, "name": "my-name", "person_age": 42},
        ]
    )
    return [
        Person(id=1, name="name1", age=22),
        Person(id=1, name="name1", age=22),
        Person(id=123, name="my-name", age=42),
    ]


@pytest.fixture(name="manager")
def get_manager(database: AsyncDatabase) -> AsyncManager:
    return AsyncManager(database=database)


@pytest.mark.usefixtures("people")
async def test_find(manager: AsyncManager, subtests):
    with subtests.test("is Person"):
        persisted = await manager.find(Person)
        assert isinstance(persisted, Person)

    with subtests.test("find by regular field"):
        persisted = await manager.find(Person, filter=Person.id == 123)
        assert persisted == Person(id=123, name="my-name", age=42)

        persisted = await manager.find(Person, filter=Person.id == 456)
        assert persisted is None

    with subtests.test("find by aliased field"):
        persisted = await manager.find(Person, filter=Person.age == 42)
        assert persisted == Person(id=123, name="my-name", age=42)

        persisted = await manager.find(Person, filter=Person.age == 99)
        assert persisted is None


@pytest.mark.usefixtures("people")
async def test_get(manager: AsyncManager, subtests):
    with subtests.test("is present"):
        persisted = await manager.get(Person, filter=Person.id == 1)
        assert isinstance(persisted, Person)

    with subtests.test("is absent"):
        with pytest.raises(NotFound):
            await manager.get(Person, filter=Person.id == 9999)


@pytest.mark.usefixtures("people")
async def test_select(manager: AsyncManager, subtests):
    with subtests.test("find by regular field"):
        iterator = manager.select(Person, filter=Person.id.in_([1, 2, 123]))
        persisted = await to_list(iterator)
        assert persisted == [
            Person(id=1, name="name1", age=22),
            Person(id=2, name="name2", age=22),
            Person(id=123, name="my-name", age=42),
        ]

    with subtests.test("find by aliased field"):
        iterator = manager.select(Person, filter=Person.age == 22)
        persisted = await to_list(iterator)
        assert persisted == [
            Person(id=1, name="name1", age=22),
            Person(id=2, name="name2", age=22),
        ]
