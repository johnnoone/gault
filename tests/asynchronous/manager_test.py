import pytest
from pymongo.asynchronous.database import AsyncDatabase

from gault.exceptions import NotFound
from gault.managers import AsyncManager, Persistence
from gault.models import Attribute, Schema, configure
from gault.utils import to_list


class Person(Schema, collection="my-collection"):
    id: Attribute[int] = configure(pk=True)
    name: Attribute[str]
    age: Attribute[int] = configure(db_alias="person_age")


@pytest.fixture(name="people")
async def get_people(database: AsyncDatabase, persistence: Persistence):
    await database.get_collection("my-collection").insert_many(
        [
            {"id": 1, "name": "name1", "person_age": 22},
            {"id": 2, "name": "name2", "person_age": 22},
            {"id": 123, "name": "my-name", "person_age": 42},
        ]
    )
    people = [
        Person(id=1, name="name1", age=22),
        Person(id=1, name="name1", age=22),
        Person(id=123, name="my-name", age=42),
    ]
    for person in people:
        persistence.mark_persisted(person)
    return people


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


async def test_insert(manager: AsyncManager, subtests):
    person = Person(id=111, name="name111", age=22)
    persisted = await manager.find(Person, filter=Person.id == 111)
    assert persisted is None

    persisted = await manager.insert(person)
    assert persisted == person

    persisted = await manager.find(Person, filter=Person.id == 111)
    assert persisted == person


async def test_save(manager: AsyncManager, subtests):
    person = Person(id=111, name="name111", age=22)
    persisted = await manager.find(Person, filter=Person.id == 111)
    assert persisted is None

    persisted = await manager.save(person)
    assert persisted == person

    persisted = await manager.find(Person, filter=Person.id == 111)
    assert persisted == person


async def test_refresh(manager: AsyncManager, subtests):
    person1 = Person(id=111, name="name111", age=22)
    person2 = Person(id=111, name="other-name", age=99)

    await manager.save(person1)

    with subtests.test("they are different"):
        assert person1 != person2

    with subtests.test("they have the same attributes"):
        await manager.refresh(person2)

        assert person1 == person2


async def test_save_with_refresh(manager: AsyncManager, subtests):
    # Simulate concurrent writes.
    # need to check that call refresh with latest data
    person = Person(id=1, name="previous-name", age=11)
    await manager.insert(person)

    # some background writes
    background = Person(id=1, name="changed-name", age=11)
    await manager.save(background, atomic=True)

    # our change
    person.age = 42

    await manager.save(person, refresh=True, atomic=True)
    assert person.name == "changed-name", "It should have took the background write"
    assert person.age == 42, "It should have changed"


async def test_save_without_refresh(manager: AsyncManager, subtests):
    # Simulate concurrent writes.
    # need to check that call refresh with latest data
    person = Person(id=1, name="previous-name", age=11)
    await manager.insert(person)

    # some background writes
    background = Person(id=1, name="changed-name", age=11)
    await manager.save(background, atomic=True)

    # our change
    person.age = 42

    await manager.save(person, refresh=False, atomic=True)
    assert person.name == "previous-name", "It should have kept the current name"
    assert person.age == 42, "It should have changed"
