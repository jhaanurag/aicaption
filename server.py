#fastapi backend

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

class EmailSchema(BaseModel):
    email: EmailStr

@app.post("/submit-email")
async def get_email(payload: EmailSchema):
    print(f"DEBUG: Sent email to {payload.email}")
    return {"message": f"Received email: {payload.email}"}
