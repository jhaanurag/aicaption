from datetime import datetime, timezone

from bson import ObjectId

from backend.dao.database import database
from backend.models.content_request import ContentRequestModel


def clean_id(doc):
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def create_request(data: dict):
    data["requested_by"] = data["requested_by"].lower()
    data["request_status"] = "PENDING"
    data["request_reject_reason"] = ""
    data["created_at"] = datetime.now(timezone.utc)
    data = ContentRequestModel(**data).model_dump(mode="json")

    result = await database.content_requests.insert_one(data)
    data["_id"] = result.inserted_id
    return clean_id(data)


async def list_requests(requested_by=None, request_status=None):
    query = {}
    if requested_by:
        query["requested_by"] = requested_by.lower()
    if request_status:
        query["request_status"] = request_status

    cursor = database.content_requests.find(query).sort("created_at", -1)
    requests = []
    async for request in cursor:
        requests.append(clean_id(request))
    return requests


async def update_request_status(request_id: str, status: str, reason: str = ""):
    if not ObjectId.is_valid(request_id):
        return None

    result = await database.content_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"request_status": status, "request_reject_reason": reason}},
    )
    if result.matched_count == 0:
        return None

    request = await database.content_requests.find_one({"_id": ObjectId(request_id)})
    return clean_id(request)
