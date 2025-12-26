from __future__ import annotations
from collections.abc import AsyncIterator

from typing import TYPE_CHECKING
import pytest
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from gault.managers import AsyncManager, Persistence, StateTracker


if TYPE_CHECKING:
    from gault.types import Document


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(name="client")
def get_client() -> AsyncMongoClient[Document]:
    dsn = "mongodb://user:pass@127.0.0.1:27017"
    return AsyncMongoClient(dsn)


@pytest.fixture(name="database")
async def get_database(
    client: AsyncMongoClient[Document],
) -> AsyncIterator[AsyncDatabase[Document]]:
    database = client.get_database("my_database")
    yield database
    filter = {"name": {"$regex": r"^(?!system\.)"}}
    collections = await database.list_collection_names(filter=filter)
    for collection in collections:
        await database.drop_collection(collection)


@pytest.fixture(name="manager")
def get_manager(
    database: AsyncDatabase[Document],
    persistence: Persistence,
    state_tracker: StateTracker,
) -> AsyncManager:
    return AsyncManager(
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
