"""
User Data Access Object - handles user CRUD operations
"""

from backend.state import userdict


def get_user(email: str):
    """Get user by email"""
    return userdict.get(email)


def set_user(email: str, credits: int, role: str):
    """Create or update user"""
    userdict[email] = {"credits": credits, "role": role}


def pop_user(email: str):
    """Delete user"""
    if email in userdict:
        del userdict[email]


def update_user_credits(email: str, credits: int):
    """Update user credits"""
    if email in userdict:
        userdict[email]["credits"] = credits


def update_user_role(email: str, role: str):
    """Update user role"""
    if email in userdict:
        userdict[email]["role"] = role
