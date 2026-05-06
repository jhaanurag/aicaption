from fastapi import APIRouter, HTTPException, Request, status

from backend.dao.request_dao import create_request, list_requests, update_request_status
from backend.schemas.requests import ApprovalRequestSchema, CaptionSchema, ReviewRequestSchema
from backend.middlewares.auth_middleware import admin, user
from backend.services.ai_service import generate_caption_text
from backend.dao.user_dao import deduct_user_credit

router = APIRouter(prefix="/captions", tags=["captions"])


@router.post("/generate")
async def generate_caption_endpoint(data: CaptionSchema, request: Request):
    current_user = await user(request)
    if current_user["max_ai_credits"] < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient AI credits")

    caption = generate_caption_text(data.product_description, data.campaign_tone)
    if not await deduct_user_credit(current_user["email_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient AI credits")

    return {"generated_caption": caption}


@router.get("/credits")
async def get_credits(request: Request):
    current_user = await user(request)
    return {"max_ai_credits": current_user["max_ai_credits"]}


@router.post("/approval-requests")
async def submit_for_approval(data: ApprovalRequestSchema, request: Request):
    current_user = await user(request)
    data = data.model_dump()
    data["requested_by"] = current_user["email_id"]
    return await create_request(data)


@router.get("/approval-requests")
async def get_approval_requests(
    request: Request,
    requested_by: str | None = None,
    request_status: str | None = "PENDING",
):
    await admin(request)
    return {"requests": await list_requests(requested_by, request_status)}


@router.get("/my-requests")
async def get_my_requests(request: Request):
    current_user = await user(request)
    return {"requests": await list_requests(requested_by=current_user["email_id"])}


@router.post("/approval-requests/review")
async def review_request(data: ReviewRequestSchema, request: Request):
    await admin(request)
    if data.status == "REJECTED" and not data.reason:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reject reason is required")

    reason = data.reason.strip() if data.reason else ""
    updated = await update_request_status(data.request_id, data.status, reason)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return updated
