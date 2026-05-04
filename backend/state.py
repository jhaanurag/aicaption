"""
Global application state - in-memory storage
"""

from backend.constants import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_CREDITS

# OTP temporary storage: {email: (otp_code, timestamp)}
tempdict = {}

# User data: {email: {credits: int, role: str}}
userdict = {DEFAULT_ADMIN_EMAIL: {"credits": DEFAULT_ADMIN_CREDITS, "role": "admin"}}

# Approval requests: {request_key: {request_data}}
content_requests = {}
