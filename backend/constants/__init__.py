"""
Configuration and constants loaded from environment variables
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OTP Configuration
OTP_VALID_SECONDS = int(os.environ["OTP_VALID_SECONDS"])

# User Credits
DEFAULT_USER_CREDITS = int(os.environ["DEFAULT_USER_CREDITS"])

# Admin Configuration
DEFAULT_ADMIN_EMAIL = os.environ["DEFAULT_ADMIN_EMAIL"]
DEFAULT_ADMIN_CREDITS = int(os.environ["DEFAULT_ADMIN_CREDITS"])
