from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class EmailSchema(BaseModel):
    email_id: EmailStr


class OTPSchema(BaseModel):
    email_id: EmailStr
    otp: str = Field(min_length=6, max_length=6)


class CaptionSchema(BaseModel):
    product_description: str = Field(min_length=3)
    campaign_tone: str = Field(min_length=2)


class CreateUserSchema(BaseModel):
    email_id: EmailStr
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    role: str = "USER"
    max_ai_credits: int = Field(ge=0)
    is_active: bool = True


class UpdateUserSchema(BaseModel):
    email_id: EmailStr
    new_email_id: Optional[EmailStr] = None
    first_name: Optional[str] = Field(default=None, min_length=1)
    last_name: Optional[str] = Field(default=None, min_length=1)
    role: Optional[str] = None
    max_ai_credits: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ReviewRequestSchema(BaseModel):
    request_id: str
    status: str
    reason: Optional[str] = None


class ApprovalRequestSchema(BaseModel):
    product_description: str = Field(min_length=3)
    campaign_tone: str = Field(min_length=2)
    generated_caption: str = Field(min_length=1)
