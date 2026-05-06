import random
import string

from fastapi import APIRouter, HTTPException, status

from backend.dao.user_dao import get_user
from backend.schemas.requests import EmailSchema, OTPSchema
from backend.services.auth_service import generate_token, store_otp, validate_otp
from backend.services.email_service import send_otp_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/submit-email")
async def submit_email(request: EmailSchema):
    user = await get_user(request.email_id)
    if not user or not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found or inactive")

    otp = "".join(random.choices(string.digits, k=6))
    store_otp(request.email_id, otp)

    try:
        send_otp_email(request.email_id, otp)
    except Exception as exc:
        print(f"Email send failed: {exc}")

    return {"message": f"OTP sent to {request.email_id}"}


@router.post("/submit-otp")
async def submit_otp(request: OTPSchema):
    if not validate_otp(request.email_id, request.otp):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    user = await get_user(request.email_id)
    if not user or not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found or inactive")

    token = generate_token(request.email_id, user["role"])
    return {"token": token, "user": user}
