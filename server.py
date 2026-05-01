#fastapi backend

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

load_dotenv()

OTP_VALID_SECONDS = int(os.environ["OTP_VALID_SECONDS"])
DEFAULT_USER_CREDITS = int(os.environ["DEFAULT_USER_CREDITS"])
DEFAULT_ADMIN_EMAIL = os.environ["DEFAULT_ADMIN_EMAIL"]
DEFAULT_ADMIN_CREDITS = int(os.environ["DEFAULT_ADMIN_CREDITS"])

tempdict = {}
userdict = {DEFAULT_ADMIN_EMAIL: {"credits": DEFAULT_ADMIN_CREDITS, "role": "admin"}}
content_requests = {}

# 15 minute valid otp
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


# verify otp
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
    # generate otp and send email
    otp = generate_otp(payload.email)
    tempdict[payload.email] = (otp, time.time())
    yag.send(
        to=payload.email,
        subject="Your OTP for AICaption",
        contents=f"Your OTP is: {otp}. It is valid for 15 minutes."
    )   
    return {"message": f"OTP sent to email: {payload.email}"}


@app.post("/submit-otp")
async def verify_otp(payload: OTPSchema):
    # verify otp and send jwt
    if verify(payload.email, payload.otp):
        if payload.email not in userdict:
            set_user(payload.email, DEFAULT_USER_CREDITS, "user")
        jwt_token = f"dummy_jwt{payload.email}"
        return {"message": "OTP verified successfully", "jwt": jwt_token}
    return {"message": "Invalid OTP"}


@app.post("/generate-caption")
async def generate_caption(payload: CaptionSchema, request: Request):
    # subtract 1 credit from user
    email = request.state.email
    user = require_user(email)
    credits = user["credits"]
    if credits <= 0:
        raise HTTPException(status_code=403, detail="Not enough credits")
    caption = generate_caption_text(payload.description, payload.tone)
    user["credits"] = credits - 1
    return {"message": "Caption generated and waiting for approval", "caption": caption}


@app.get("/credits")
async def get_credits(request: Request):
    email = request.state.email
    user = require_user(email)
    return {"credits": user["credits"]}


@app.post("/send-for-approval")
async def send_for_approval(payload: ApprovalRequestSchema, request: Request):
    # post send for approval
    email = request.state.email
    require_user(email)
    request_key = next_request_key(payload.requested_by)
    content_requests[request_key] = {
        "requested_by": payload.requested_by,
        "product_desc": payload.product_desc,
        "tone": payload.tone,
        "generated_caption": payload.generated_caption,
        "request_status": "pending",
        "request_reason_rejected": None,
        "created_at": time.time()
    }
    return {"message": "Content sent for approval"}


@app.get("/all-requests")
async def all_requests(request: Request):
    # get all requests for admin
    email = request.state.email
    require_admin(email)
    return {"all_requests": content_requests}


@app.get("/my-requests")
async def my_requests(request: Request):
    # get all requests for user
    email = request.state.email
    require_user(email)
    return {
        "requests": [
            request_item for request_item in content_requests.values()
            if request_item["requested_by"] == email
        ]
    }


@app.post("/review-request")
async def review_request(payload: ReviewRequestSchema, request: Request):
    # post approve/reject with reason
    email = request.state.email
    require_admin(email)

    request_key = None
    for key, request_item in content_requests.items():
        if request_item["requested_by"] == payload.email_to_review:
            request_key = key
            break

    if request_key is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if payload.approve:
        content_requests[request_key]["request_status"] = "approved"
        content_requests[request_key]["request_reason_rejected"] = None
    else:
        if not payload.reason:
            raise HTTPException(status_code=422, detail="Reject reason is required")
        content_requests[request_key]["request_status"] = "rejected"
        content_requests[request_key]["request_reason_rejected"] = payload.reason
    
    return {"message": "Request reviewed successfully"}


@app.get("/all-users")
async def all_users(request: Request):
    # admin get all users details
    email = request.state.email
    require_admin(email)
    return {"users": userdict}


@app.post("/update-user")
async def update_user(payload: UpdateUserSchema, request: Request):
    # update user details only admin can
    email = request.state.email
    require_admin(email)
    user = require_user(payload.email_to_update)
    
    current_email = payload.email_to_update
    if payload.new_email:
        userdict[payload.new_email] = dict(user)
        pop_user(current_email)
        current_email = payload.new_email

    if payload.new_credits is not None:
        userdict[current_email]["credits"] = payload.new_credits

    if payload.new_role is not None:
        userdict[current_email]["role"] = payload.new_role
    
    return {"message": "User updated successfully"}


@app.post("/delete-user")
async def delete_user(request: Request, email_to_delete: EmailStr):
    # admin delete user
    email = request.state.email
    require_admin(email)
    require_user(email_to_delete)
    
    pop_user(email_to_delete)
    
    return {"message": "User deleted successfully"}


@app.post("/create-user")
async def create_user(payload: CreateUserSchema, request: Request):
    # admin create user
    email = request.state.email
    require_admin(email)
    if payload.email in userdict:
        raise HTTPException(status_code=400, detail="User already exists")
    
    set_user(payload.email, payload.credits, payload.role)
    
    return {"message": "User created successfully"}
