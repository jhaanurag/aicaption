import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.constants import MONGODB_DB_NAME, MONGODB_URI

client: AsyncIOMotorClient = AsyncIOMotorClient(MONGODB_URI, tlsCAFile=certifi.where())
database: AsyncIOMotorDatabase = client[MONGODB_DB_NAME]


async def ensure_indexes() -> None:
    await database.users.create_index("email_id", unique=True)
    await database.content_requests.create_index([("requested_by", 1), ("created_at", -1)])
    await database.content_requests.create_index([("request_status", 1), ("created_at", -1)])
