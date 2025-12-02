import pytest
from mongo_odm.managers import Persistence
from mongo_odm.managers import AsyncManager
from mongo_odm.models import Model, configure


@pytest.fixture(name="persistence")
def get_persistence() -> Persistence:
    return Persistence()


class MyModel(Model, collection="my-collection"):
    id: int = configure(pk=True)
    name: str
    tags: list[str]


def test_not_persisted(persistence: Persistence):
    instance = MyModel(id=1, name="my-name", tags=["tag1", "tag2"])

    assert persistence.is_persisted(instance) is False


def test_force_persisted(persistence: Persistence):
    instance = MyModel(id=1, name="my-name", tags=["tag1", "tag2"])
    assert persistence.is_persisted(instance) is False

    persistence.mark_persisted(instance)

    assert persistence.is_persisted(instance) is True


def test_forget_persistence(persistence: Persistence):
    instance = MyModel(id=1, name="my-name", tags=["tag1", "tag2"])
    persistence.mark_persisted(instance)
    assert persistence.is_persisted(instance) is True

    persistence.forget(instance)

    assert persistence.is_persisted(instance) is False


async def test_persist_when_inserted(manager: AsyncManager):
    instance = MyModel(id=1, name="my-name", tags=["tag1", "tag2"])
    assert manager.persistence.is_persisted(instance) is False
    await manager.insert(instance)

    assert manager.persistence.is_persisted(instance) is True


async def test_persist_when_saved(manager: AsyncManager):
    instance = MyModel(id=1, name="my-name", tags=["tag1", "tag2"])
    assert manager.persistence.is_persisted(instance) is False
    await manager.save(instance)

    assert manager.persistence.is_persisted(instance) is True
