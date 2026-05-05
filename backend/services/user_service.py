"""
User Service - handles user registration, credits, and role management
"""

from backend.dao.user_dao import get_user, set_user, update_user_credits
from backend.constants import DEFAULT_USER_CREDITS


def register_user(email: str):
    """Register new user with default credits"""
    if not get_user(email):
        set_user(email, DEFAULT_USER_CREDITS, "user")
        return True
    return False


def get_user_details(email: str):
    """Get user info"""
    return get_user(email)


def deduct_credits(email: str, amount: int) -> bool:
    """Deduct credits, return True if successful"""
    user = get_user(email)
    if not user or user["credits"] < amount:
        return False
    
    update_user_credits(email, user["credits"] - amount)
    return True


def add_credits(email: str, amount: int):
    """Add credits to user"""
    user = get_user(email)
    if user:
        update_user_credits(email, user["credits"] + amount)


def has_sufficient_credits(email: str, amount: int) -> bool:
    """Check if user has enough credits"""
    user = get_user(email)
    return user and user["credits"] >= amount
