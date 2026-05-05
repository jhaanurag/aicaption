"""
Authentication Service - handles JWT token generation and OTP validation
"""

import time
from backend.dao.user_dao import get_user
from backend.state import tempdict
from backend.constants import OTP_VALID_SECONDS


def generate_token(email: str) -> str:
    """Generate dummy JWT token"""
    return f"dummy_jwt{email}"


def validate_otp(email: str, otp: str) -> bool:
    """Validate OTP against stored value"""
    if email not in tempdict:
        return False
    
    stored_otp, timestamp = tempdict[email]
    if stored_otp != otp:
        return False
    
    # Check if OTP expired
    if time.time() - timestamp > OTP_VALID_SECONDS:
        del tempdict[email]
        return False
    
    del tempdict[email]
    return True


def store_otp(email: str, otp: str):
    """Store OTP with timestamp"""
    tempdict[email] = (otp, time.time())


def validate_token(token: str) -> str | None:
    """Extract email from token, None if invalid"""
    if not token.startswith("dummy_jwt"):
        return None
    return token.replace("dummy_jwt", "")


def check_user_exists(email: str) -> bool:
    """Check if user exists"""
    return get_user(email) is not None
