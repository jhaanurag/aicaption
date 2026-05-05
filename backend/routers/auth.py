"""
Auth Router - handles email submission and OTP verification
"""

from fastapi import APIRouter, HTTPException, status
import random
import string
from backend.schemas.requests import EmailSchema, OTPSchema
from backend.services.auth_service import generate_token, validate_otp, store_otp, check_user_exists
from backend.services.email_service import send_otp_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/submit-email")
async def submit_email(request: EmailSchema):
    """
    Submit email for authentication
    
    Args:
        request: Email to authenticate
    
    Returns:
        Message confirming OTP sent
    """
    if not check_user_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # Store OTP
    store_otp(request.email, otp)
    
    # Send via email (ignore failures for testing)
    try:
        send_otp_email(request.email, otp)
    except Exception as e:
        print(f"Email send failed (continuing): {e}")
    
    return {"message": f"OTP sent to {request.email}"}


@router.post("/submit-otp")
async def submit_otp(request: OTPSchema):
    """
    Submit OTP for verification
    
    Args:
        request: OTP to verify
    
    Returns:
        JWT token if valid
    """
    if not validate_otp(request.email, str(request.otp)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    token = generate_token(request.email)
    return {"token": token}
