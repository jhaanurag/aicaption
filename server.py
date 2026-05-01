# fastapi backend

import os
import random
import time
from typing import Optional

import yagmail
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from ai_service import generate_caption_text

app = FastAPI()

OTP_VALID_SECONDS = 900
DEFAULT_USER_CREDITS = 5
DEFAULT_ADMIN_EMAIL = "fulfutureful@gmail.com"
DEFAULT_ADMIN_CREDITS = 10

tempdict = {}
userdict = {DEFAULT_ADMIN_EMAIL: {"credits": DEFAULT_ADMIN_CREDITS, "role": "admin"}}
content_requests = {}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/submit-email", "/submit-otp"]:
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401, 
            content={"detail": "Not authenticated"}
        )
    
    token = auth_header.split(" ")[1]
    if "dummy_jwt" not in token:
        return JSONResponse(
            status_code=401, 
            content={"detail": "Invalid token"}
        )
    
    request.state.email = token.split("dummy_jwt")[1]

    return await call_next(request)

load_dotenv()

yag = yagmail.SMTP(os.getenv("GMAIL_ID"), os.getenv("APP_PASSWORD"))


class EmailSchema(BaseModel):
    email: EmailStr


class OTPSchema(BaseModel):
    email: EmailStr
    otp: int


class CaptionSchema(BaseModel):
    description: str
    tone: str


class CreateUserSchema(BaseModel):
    email: EmailStr
    credits: int
    role: str = "user"


class UpdateUserSchema(BaseModel):
    email_to_update: EmailStr
    new_email: Optional[EmailStr] = None
    new_credits: Optional[int] = None
    new_role: Optional[str] = None


class ReviewRequestSchema(BaseModel):
    email_to_review: EmailStr
    approve: bool
    reason: Optional[str] = None


class ApprovalRequestSchema(BaseModel):
    requested_by: EmailStr
    product_desc: str
    tone: str
    generated_caption: str

def generate_otp(email):
    otp = random.randint(100000, 999999)
    tempdict[email] = (otp, time.time())
    return otp


def verify(email, otp):
    if email in tempdict:
        stored_otp, timestamp = tempdict[email]
        if time.time() - timestamp < OTP_VALID_SECONDS and stored_otp == otp:
            del tempdict[email]
            return True
    return False


def get_user(email):
    return userdict.get(email)


def require_user(email):
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def require_admin(email):
    user = require_user(email)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return user


def set_user(email, credits, role):
    userdict[email] = {"credits": credits, "role": role}


def pop_user(email):
    if email in userdict:
        del userdict[email]


def next_request_key(email):
    return f"{email}:{int(time.time() * 1000)}"


@app.post("/submit-email")
async def get_email(payload: EmailSchema):
    # generate the otp and send email and save otp with timestamp keyed by email
    otp = generate_otp(payload.email)
    tempdict[payload.email] = (otp,time.time())
    yag.send(
        to=payload.email,
        subject='Your OTP for AICaption',
        contents=f'Your OTP is: {otp}. It is valid for 15 minutes.'
    )   
    return {"message": f"OTP sent to email: {payload.email}"}

@app.post("/submit-otp")
async def verify_otp(payload: OTPSchema):
    #verify otp
    if verify(payload.email, payload.otp):
        #generate jwt with role mentioned and send to frontend
        if payload.email not in userdict:
            userdict[payload.email] = (5, "user")
        jwt_token = "dummy_jwt" + payload.email
        return {"message": "OTP verified successfully", "jwt": jwt_token}
    return {"message": "Invalid OTP"}


# post the product desc: str and tone: str to backend only auth users can 
# return generated caption and save the generated caption
@app.post("/generate-caption")
async def generate_caption(payload: CaptionSchema, request: Request):
    email = request.state.email
    # subtract 1 credit from user
    credits, role = userdict[email]
    if credits <= 0:
        raise HTTPException(status_code=403, detail="Not enough credits")
    caption = generate_caption_text(payload.description, payload.tone)
    userdict[email] = (credits - 1, role)
    return {"message": "Caption generated and waiting for approval", "caption": caption}

# get credits
@app.get("/credits")
async def get_credits(request: Request):
    email = request.state.email
    credits, role = userdict[email]
    return {"credits": credits}

# post send for approval
@app.post("/send-for-approval")
async def send_for_approval(request: Request):
    email = request.state.email
    content_requests[email] = {
        "requested_by": email,
        "product_desc": "desc",
        "tone": "tone",
        "request_status": "pending",
        "created_at": time.time()
    }
    return {"message": "Content sent for approval"}

# get all requests for admin
@app.get("/all-requests")
async def all_requests(request: Request):
    email = request.state.email
    credits, role = userdict[email]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"all_requests": content_requests}

# post approve/reject with reason
@app.post("/review-request")
async def review_request(request: Request, email_to_review: EmailStr, approve: bool, reason: str = None):
    email = request.state.email
    credits, role = userdict[email]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if email_to_review not in content_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if approve:
        content_requests[email_to_review]["request_status"] = "approved"
    else:
        content_requests[email_to_review]["request_status"] = "rejected"
        content_requests[email_to_review]["request_reason_rejected"] = reason
    
    return {"message": "Request reviewed successfully"}

#admin get all users details
@app.get("/all-users")
async def all_users(request: Request):
    email = request.state.email
    credits, role = userdict[email]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"users": userdict}

#update user details can be any combination like only email or email or credits or other stuff only admin can
@app.post("/update-user")
async def update_user(request: Request, email_to_update: EmailStr, new_email: EmailStr = None, new_credits: int = None):
    email = request.state.email
    credits, role = userdict[email]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if email_to_update not in userdict:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_credits, current_role = userdict[email_to_update]
    if new_email:
        userdict[new_email] = (current_credits, current_role)
        del userdict[email_to_update]
    if new_credits is not None:
        userdict[email_to_update] = (new_credits, current_role)
    
    return {"message": "User updated successfully"}

#admin delete user
@app.post("/delete-user")
async def delete_user(request: Request, email_to_delete: EmailStr):
    email = request.state.email
    credits, role = userdict[email]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if email_to_delete not in userdict:
        raise HTTPException(status_code=404, detail="User not found")
    
    del userdict[email_to_delete]
    
    return {"message": "User deleted successfully"}

#admin create user
@app.post("/create-user")
async def create_user(request: Request, email_to_create: EmailStr, credits: int, role: str):
    email = request.state.email
    credits, role = userdict[email]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if email_to_create in userdict:
        raise HTTPException(status_code=400, detail="User already exists")
    
    userdict[email_to_create] = (credits, role)
    
    return {"message": "User created successfully"}
