"""
Pydantic request and response models for validation
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """Email submission for OTP request"""
    email: EmailStr


class OTPSchema(BaseModel):
    """OTP verification request"""
    email: EmailStr
    otp: int


class CaptionSchema(BaseModel):
    """Caption generation request"""
    description: str
    tone: str


class CreateUserSchema(BaseModel):
    """Create new user (admin only)"""
    email: EmailStr
    credits: int
    role: str = "user"


class UpdateUserSchema(BaseModel):
    """Update user details (admin only)"""
    email_to_update: EmailStr
    new_email: Optional[EmailStr] = None
    new_credits: Optional[int] = None
    new_role: Optional[str] = None


class ReviewRequestSchema(BaseModel):
    """Approve or reject approval request (admin only)"""
    email_to_review: EmailStr
    approve: bool
    reason: Optional[str] = None


class ApprovalRequestSchema(BaseModel):
    """Submit content for approval"""
    requested_by: EmailStr
    product_desc: str
    tone: str
    generated_caption: str
