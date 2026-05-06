from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    email_id: EmailStr
    first_name: str
    last_name: str
    role: str = "USER"
    max_ai_credits: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
