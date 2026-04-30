# generate a random 6 digit numeric pin:
import random

# In-memory storage for OTPs (for demonstration, replace with a database for production)
otp_storage = {}

# only valid for 15 min (handled by external logic or timestamp check in production)
def generate_otp(email):
    otp = random.randint(100000, 999999)
    otp_storage[email] = str(otp)
    return otp

# verify otp
def verify_otp(email, otp):
    stored_otp = otp_storage.get(email)
    if stored_otp and stored_otp == str(otp):
        del otp_storage[email]
        return True
    return False