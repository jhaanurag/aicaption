"""
Request Data Access Object - handles approval request CRUD operations
"""

import time
from backend.state import content_requests


def next_request_key(email: str) -> str:
    """Generate unique request key"""
    return f"{email}:{int(time.time() * 1000)}"


def create_request(request_key: str, request_data: dict):
    """Store approval request"""
    content_requests[request_key] = request_data


def get_request(request_key: str):
    """Get request by key"""
    return content_requests.get(request_key)


def get_all_requests():
    """Get all requests"""
    return content_requests


def get_user_requests(email: str):
    """Get all requests by user"""  
    return [req for req in content_requests.values() if req["requested_by"] == email]


def find_request_by_email(email: str):
    """Find first request key for user"""
    for key, request_item in content_requests.items():
        if request_item["requested_by"] == email:
            return key
    return None


def update_request_status(request_key: str, status: str, reason: str = None):
    """Update request status (approved/rejected) and optional reason"""
    if request_key in content_requests:
        content_requests[request_key]["request_status"] = status
        content_requests[request_key]["request_reason_rejected"] = reason
