from collections.abc import Iterator

import pytest
from pymongo.synchronous.database import Database
from pymongo.synchronous.mongo_client import MongoClient

from strata.managers import Manager, Persistence, StateTracker


@pytest.fixture(name="client")
def get_client() -> MongoClient:
    dsn = "mongodb://user:pass@127.0.0.1:27017"
    return MongoClient(dsn)


@pytest.fixture(name="database")
def get_database(client) -> Iterator[Database]:
    database = client.get_database("my_database")
    yield database
    filter = {"name": {"$regex": r"^(?!system\.)"}}
    collections = database.list_collection_names(filter=filter)
    for collection in collections:
        database.drop_collection(collection)


@pytest.fixture(name="manager")
def get_manager(
    database: Database,
    persistence: Persistence,
    state_tracker: StateTracker,
) -> Manager:
    return Manager(
        database=database, persistence=persistence, state_tracker=state_tracker
    )


@pytest.fixture(name="persistence")
def get_persistence() -> Persistence:
    return Persistence()


@pytest.fixture(name="state_tracker")
def get_state_tracker():
    return StateTracker()


@pytest.fixture(name="context")
def get_context():
    return {}
