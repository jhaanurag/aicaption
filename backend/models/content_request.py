from datetime import datetime

from pydantic import BaseModel, EmailStr


class ContentRequestModel(BaseModel):
    requested_by: EmailStr
    product_description: str
    campaign_tone: str
    generated_caption: str
    request_status: str = "PENDING"
    request_reject_reason: str = ""
    created_at: datetime
