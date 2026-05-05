"""
Email Service - sends OTP emails using GMAIL_USER and GMAIL_PASSWORD
"""

import os
import yagmail


def send_otp_email(email: str, otp: str):
    """Send OTP to email"""
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")
    
    if not gmail_user or not gmail_password:
        raise ValueError("Gmail credentials not configured in .env")
    
    subject = "Your OTP Code"
    body = f"""
    Your OTP Code: {otp}
    
    Please use this code to verify your email.
    This code is valid for a limited time.
    """
    
    try:
        yag = yagmail.SMTP(gmail_user, gmail_password)
        yag.send(to=email, subject=subject, contents=body)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
