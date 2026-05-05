"""
Caption Router - handles caption generation and approval workflow
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.requests import CaptionSchema, ReviewRequestSchema, ApprovalRequestSchema
from backend.services.caption_service import generate_caption
from backend.services.user_service import deduct_credits, has_sufficient_credits
from backend.dao.request_dao import (
    create_request, get_all_requests, update_request_status, 
    get_user_requests, next_request_key
)
from backend.middlewares.auth_middleware import verify_token, require_admin

router = APIRouter(prefix="/caption", tags=["caption"])


@router.post("/generate-caption")
async def generate_caption_endpoint(
    request: CaptionSchema,
    email: str = Depends(verify_token)
):
    """
    Generate caption for image description (costs 1 credit)
    
    Args:
        request: Image description and tone
        email: Authenticated user email
    
    Returns:
        Generated caption text
    """
    if not has_sufficient_credits(email, 1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient credits"
        )
    
    # Generate caption
    caption = generate_caption(request.description, request.tone)
    
    # Deduct credit
    deduct_credits(email, 1)
    
    return {"caption": caption}


@router.get("/credits")
async def get_credits(email: str = Depends(verify_token)):
    """
    Get user's remaining credits
    
    Args:
        email: Authenticated user email
    
    Returns:
        Remaining credit count
    """
    from backend.dao.user_dao import get_user
    
    user = get_user(email)
    return {"credits": user["credits"]}


@router.post("/send-for-approval")
async def send_for_approval(
    request: ApprovalRequestSchema,
    email: str = Depends(verify_token)
):
    """
    Send caption for admin approval
    
    Args:
        request: Caption and description to approve
        email: Authenticated user email
    
    Returns:
        Request ID for tracking
    """
    request_id = next_request_key()
    
    create_request(
        request_id,
        {
            "requested_by": email,
            "description": request.description,
            "caption": request.caption,
            "request_status": "pending"
        }
    )
    
    return {"request_id": request_id, "status": "pending"}


@router.get("/all-requests")
async def get_all_requests_endpoint(
    admin_email: str = Depends(require_admin)
):
    """
    Get all approval requests (admin only)
    
    Args:
        admin_email: Admin email (verified by middleware)
    
    Returns:
        All pending/approved/rejected requests
    """
    from backend.state import content_requests
    return {"requests": content_requests}


@router.get("/my-requests")
async def get_my_requests(
    email: str = Depends(verify_token)
):
    """
    Get user's own approval requests
    
    Args:
        email: Authenticated user email
    
    Returns:
        User's requests with statuses
    """
    requests = get_user_requests(email)
    return {"requests": requests}


@router.post("/review-request")
async def review_request(
    request: ReviewRequestSchema,
    admin_email: str = Depends(require_admin)
):
    """
    Review and approve/reject caption request (admin only)
    
    Args:
        request: Request ID, approval status, and reason
        admin_email: Admin email (verified by middleware)
    
    Returns:
        Updated request status
    """
    update_request_status(
        request_id=request.request_id,
        status=request.status,
        reason=request.reason
    )
    
    return {"request_id": request.request_id, "status": request.status}
