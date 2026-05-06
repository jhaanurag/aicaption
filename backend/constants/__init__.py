import os
from dotenv import load_dotenv

load_dotenv()

OTP_VALID_SECONDS = int(os.environ["OTP_VALID_SECONDS"])

DEFAULT_USER_CREDITS = int(os.environ["DEFAULT_USER_CREDITS"])

DEFAULT_ADMIN_EMAIL = os.environ["DEFAULT_ADMIN_EMAIL"]
DEFAULT_ADMIN_CREDITS = int(os.environ["DEFAULT_ADMIN_CREDITS"])

MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URI", "mongodb://localhost:27017"))
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_caption")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE_SECONDS", "86400"))
