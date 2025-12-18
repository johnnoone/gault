from strata.managers import AsyncManager, StateTracker
from strata.models import Attribute, Schema


class MyModel(Schema, collection="my-collection"):
    id: Attribute[int]
    name: Attribute[str]
    age: Attribute[int]


def test_get_dirty_fields(state_tracker: StateTracker):
    instance = MyModel(id="string", name=124, age=24)

    state_tracker.snapshot(instance)
    assert state_tracker.get_dirty_fields(instance) == set()

    instance.age = 99
    assert state_tracker.get_dirty_fields(instance) == {"age"}

    instance.age = 24
    assert state_tracker.get_dirty_fields(instance) == set()


def test_reset(state_tracker: StateTracker):
    instance = MyModel(id="string", name=124, age=24)
    state_tracker.snapshot(instance)

    instance.age = 99
    assert state_tracker.get_dirty_fields(instance) == {"age"}

    state_tracker.reset(instance)

    assert instance.age == 24
    assert state_tracker.get_dirty_fields(instance) == set()


async def test_snapshot_when_select(manager: AsyncManager, state_tracker):
    instance = MyModel(id=123, name="my-name", age=24)
    await manager.insert(instance)

    persisted = await manager.get(MyModel, MyModel.id == 123)
    assert manager.state_tracker.get_dirty_fields(persisted) == set()

    persisted.age = 24
    assert manager.state_tracker.get_dirty_fields(persisted) == set()

    persisted.age = 99
    assert manager.state_tracker.get_dirty_fields(persisted) == {"age"}
