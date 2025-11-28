import pytest

from collections.abc import AsyncIterator
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from mongo_odm import AsyncManager


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(name="client")
def get_client() -> AsyncMongoClient:
    dsn = "mongodb://user:pass@127.0.0.1:27017"
    return AsyncMongoClient(dsn)


@pytest.fixture(name="database")
async def get_database(client) -> AsyncIterator[AsyncDatabase]:
    database = client.get_database("my_database")
    yield database
    filter = {"name": {"$regex": r"^(?!system\.)"}}
    collections = await database.list_collection_names(filter=filter)
    for collection in collections:
        await database.drop_collection(collection)


@pytest.fixture(name="manager")
def get_manager(database: AsyncDatabase) -> AsyncManager:
    return AsyncManager(database=database)
