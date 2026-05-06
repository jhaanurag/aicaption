from datetime import datetime, timezone

from backend.dao.database import database
from backend.models.user import UserModel


def clean_id(doc):
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def get_user(email_id: str):
    user = await database.users.find_one({"email_id": email_id.lower()})
    return clean_id(user)


async def create_user(data: dict):
    now = datetime.now(timezone.utc)
    data["email_id"] = data["email_id"].lower()
    data["created_at"] = now
    data["updated_at"] = now
    data = UserModel(**data).model_dump(mode="json")

    result = await database.users.insert_one(data)
    data["_id"] = result.inserted_id
    return clean_id(data)


async def upsert_admin(email_id: str, credits: int):
    now = datetime.now(timezone.utc)
    admin_data = UserModel(
        email_id=email_id.lower(),
        first_name="System",
        last_name="Admin",
        role="ADMIN",
        max_ai_credits=credits,
        is_active=True,
        created_at=now,
        updated_at=now,
    ).model_dump(mode="json")

    await database.users.update_one(
        {"email_id": email_id.lower()},
        {
            "$setOnInsert": {
                "email_id": admin_data["email_id"],
                "first_name": admin_data["first_name"],
                "last_name": admin_data["last_name"],
                "role": admin_data["role"],
                "created_at": admin_data["created_at"],
            },
            "$set": {
                "max_ai_credits": admin_data["max_ai_credits"],
                "is_active": admin_data["is_active"],
                "updated_at": admin_data["updated_at"],
            },
        },
        upsert=True,
    )


async def list_users(is_active=None):
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    cursor = database.users.find(query).sort("email_id", 1)
    users = []
    async for user in cursor:
        users.append(clean_id(user))
    return users


async def update_user(email_id: str, updates: dict):
    updates = {key: value for key, value in updates.items() if value is not None}
    if not updates:
        return await get_user(email_id)

    updates["updated_at"] = datetime.now(timezone.utc)
    result = await database.users.update_one({"email_id": email_id.lower()}, {"$set": updates})
    if result.matched_count == 0:
        return None
    return await get_user(updates.get("email_id", email_id))


async def deduct_user_credit(email_id: str):
    result = await database.users.update_one(
        {"email_id": email_id.lower(), "max_ai_credits": {"$gt": 0}, "is_active": True},
        {"$inc": {"max_ai_credits": -1}, "$set": {"updated_at": datetime.now(timezone.utc)}},
    )
    return result.modified_count == 1
