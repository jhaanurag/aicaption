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
    
    token = auth_header.split(" ")[1]
    if "dummy_jwt" not in token:
        return JSONResponse(
            status_code=401, 
            content={"detail": "Invalid token"}
        )

    return await call_next(request)

tempdict = {}
admin_email = "admin@admin.com"

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
        jwt_token = "dummy_jwt" + payload.email
        return {"message": "OTP verified successfully", "jwt": jwt_token}
    return {"message": "Invalid OTP"}


# post the product desc and tone to backend only auth users can 
# return generated caption and save the generated caption

# post send for approval




 
