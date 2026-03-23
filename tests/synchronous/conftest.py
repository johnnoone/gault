from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest
from gault.managers import Manager, Persistence, StateTracker
from pymongo.synchronous.database import Database
from pymongo.synchronous.mongo_client import MongoClient

if TYPE_CHECKING:
    from gault.types import Document


@pytest.fixture(name="client")
def get_client(mongodb_dsn: str) -> MongoClient[Document]:
    return MongoClient(mongodb_dsn)


@pytest.fixture(name="database")
def get_database(client: MongoClient[Document]) -> Iterator[Database]:
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
