import pytest
from pymongo.synchronous.database import Database

from strata.exceptions import NotFound
from strata.managers import Manager, Persistence
from strata.models import Attribute, Schema, configure
from strata.utils import to_list


class Person(Schema, collection="my-collection"):
    id: Attribute[int] = configure(pk=True)
    name: Attribute[str]
    age: Attribute[int] = configure(db_alias="person_age")


@pytest.fixture(name="people")
def get_people(database: Database, persistence: Persistence):
    database.get_collection("my-collection").insert_many(
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
def test_find(manager: Manager, subtests):
    with subtests.test("is Person"):
        persisted = manager.find(Person)
        assert isinstance(persisted, Person)

    with subtests.test("find by regular field"):
        persisted = manager.find(Person, filter=Person.id == 123)
        assert persisted == Person(id=123, name="my-name", age=42)

        persisted = manager.find(Person, filter=Person.id == 456)
        assert persisted is None

    with subtests.test("find by aliased field"):
        persisted = manager.find(Person, filter=Person.age == 42)
        assert persisted == Person(id=123, name="my-name", age=42)

        persisted = manager.find(Person, filter=Person.age == 99)
        assert persisted is None


@pytest.mark.usefixtures("people")
def test_get(manager: Manager, subtests):
    with subtests.test("is present"):
        persisted = manager.get(Person, filter=Person.id == 1)
        assert isinstance(persisted, Person)

    with subtests.test("is absent"):
        with pytest.raises(NotFound):
            manager.get(Person, filter=Person.id == 9999)


@pytest.mark.usefixtures("people")
def test_select(manager: Manager, subtests):
    with subtests.test("find by regular field"):
        iterator = manager.select(Person, filter=Person.id.in_([1, 2, 123]))
        persisted = list(iterator)
        assert persisted == [
            Person(id=1, name="name1", age=22),
            Person(id=2, name="name2", age=22),
            Person(id=123, name="my-name", age=42),
        ]

    with subtests.test("find by aliased field"):
        iterator = manager.select(Person, filter=Person.age == 22)
        persisted = list(iterator)
        assert persisted == [
            Person(id=1, name="name1", age=22),
            Person(id=2, name="name2", age=22),
        ]


def test_insert(manager: Manager, subtests):
    person = Person(id=111, name="name111", age=22)
    persisted = manager.find(Person, filter=Person.id == 111)
    assert persisted is None

    persisted = manager.insert(person)
    assert persisted == person

    persisted = manager.find(Person, filter=Person.id == 111)
    assert persisted == person


def test_save(manager: Manager, subtests):
    person = Person(id=111, name="name111", age=22)
    persisted = manager.find(Person, filter=Person.id == 111)
    assert persisted is None

    persisted = manager.save(person)
    assert persisted == person

    persisted = manager.find(Person, filter=Person.id == 111)
    assert persisted == person


def test_refresh(manager: Manager, subtests):
    person1 = Person(id=111, name="name111", age=22)
    person2 = Person(id=111, name="other-name", age=99)

    manager.save(person1)

    with subtests.test("they are different"):
        assert person1 != person2

    with subtests.test("they have the same attributes"):
        manager.refresh(person2)

        assert person1 == person2


def test_save_with_refresh(manager: Manager, subtests):
    # Simulate concurrent writes.
    # need to check that call refresh with latest data
    person = Person(id=1, name="previous-name", age=11)
    manager.insert(person)

    # some background writes
    background = Person(id=1, name="changed-name", age=11)
    manager.save(background, atomic=True)

    # our change
    person.age = 42

    manager.save(person, refresh=True, atomic=True)
    assert person.name == "changed-name", "It should have took the background write"
    assert person.age == 42, "It should have changed"


def test_save_without_refresh(manager: Manager, subtests):
    # Simulate concurrent writes.
    # need to check that call refresh with latest data
    person = Person(id=1, name="previous-name", age=11)
    manager.insert(person)

    # some background writes
    background = Person(id=1, name="changed-name", age=11)
    manager.save(background, atomic=True)

    # our change
    person.age = 42

    manager.save(person, refresh=False, atomic=True)
    assert person.name == "previous-name", "It should have kept the current name"
    assert person.age == 42, "It should have changed"
