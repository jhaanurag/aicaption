from datetime import datetime, timedelta, timezone

import jwt

from backend.constants import JWT_ALGORITHM, JWT_EXPIRE_SECONDS, JWT_SECRET_KEY, OTP_VALID_SECONDS

otp_store = {}


def generate_token(email_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email_id.lower(),
        "role": role,
        "iat": now,
        "exp": now + timedelta(seconds=JWT_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def validate_otp(email_id: str, otp: str) -> bool:
    email_id = email_id.lower()
    if email_id not in otp_store:
        return False

    stored_otp, timestamp = otp_store[email_id]
    if stored_otp != otp:
        return False

    if datetime.now(timezone.utc).timestamp() - timestamp > OTP_VALID_SECONDS:
        del otp_store[email_id]
        return False

    del otp_store[email_id]
    return True


def store_otp(email_id: str, otp: str) -> None:
    otp_store[email_id.lower()] = (otp, datetime.now(timezone.utc).timestamp())


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
