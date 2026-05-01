#fastapi backend

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import random
import time
import os
from dotenv import load_dotenv
import yagmail

app = FastAPI()

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
    
    # 3. Simple validation and attach user to request state
    token = auth_header.split(" ")[1]
    if "dummy_jwt" not in token:
        return JSONResponse(
            status_code=401, 
            content={"detail": "Invalid token"}
        )
    
    # Attach the email (extracted from token) to the request context
    request.state.email = token.split("dummy_jwt")[1]

    return await call_next(request)

tempdict = {}
temp_admin_email = "fulfutureful@gmail.com"
userdict = {temp_admin_email: (10, "admin")} # email: (credits, role)
content_requests  = {} #requested_by , product_desc, tone, caption, request_status=pending/approved/rejected, request_reason_rejected, created_at)

load_dotenv()

yag = yagmail.SMTP(os.getenv('GMAIL_ID'), os.getenv('APP_PASSWORD'))

# 15 minute valid otp
def generate_otp(email):
    otp = random.randint(100000, 999999)
    tempdict[email] = (otp, time.time())
    return otp

def verify(email, otp):
    if email in tempdict:
        stored_otp, timestamp = tempdict[email]
        if time.time() - timestamp < 900 and stored_otp == otp:
            del tempdict[email]
            return True
    return False

class EmailSchema(BaseModel):
    email: EmailStr

class OTPSchema(BaseModel):
    email: EmailStr
    otp: int

class CaptionSchema(BaseModel):
    description: str
    tone: str


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
    caption = f"Generated caption for {payload.description} with {payload.tone} tone"
    # subtract 1 credit from user
    credits, role = userdict[email]
    if credits <= 0:
        raise HTTPException(status_code=403, detail="Not enough credits")
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

# get all pending requests for admin
@app.get("/pending-requests")
async def pending_requests(request: Request):
    email = request.state.email
    credits, role = userdict[email]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    pending = {k:v for k,v in content_requests.items() if v["request_status"] == "pending"}
    return {"pending_requests": pending}

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

