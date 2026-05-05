"""
User Router - handles user management (admin only)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.requests import CreateUserSchema, UpdateUserSchema
from backend.services.user_service import register_user
from backend.dao.user_dao import (
    get_user, set_user, pop_user, update_user_role
)
from backend.state import userdict
from backend.middlewares.auth_middleware import require_admin

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create-user")
async def create_user(
    request: CreateUserSchema,
    admin_email: str = Depends(require_admin)
):
    """
    Create new user (admin only)
    
    Args:
        request: User email and initial credits
        admin_email: Admin email (verified by middleware)
    
    Returns:
        New user details
    """
    if get_user(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    set_user(request.email, request.credits, "user")
    
    return {"email": request.email, "credits": request.credits, "role": "user"}


@router.post("/delete-user")
async def delete_user(
    request: CreateUserSchema,
    admin_email: str = Depends(require_admin)
):
    """
    Delete user (admin only)
    
    Args:
        request: User email to delete
        admin_email: Admin email (verified by middleware)
    
    Returns:
        Deletion confirmation
    """
    if not pop_user(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    return {"message": f"User {request.email} deleted"}


@router.post("/update-user")
async def update_user(
    request: UpdateUserSchema,
    admin_email: str = Depends(require_admin)
):
    """
    Update user credits or role (admin only)
    
    Args:
        request: User email and new credits/role
        admin_email: Admin email (verified by middleware)
    
    Returns:
        Updated user details
    """
    user = get_user(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    if request.credits is not None:
        user["credits"] = request.credits
    
    if request.role is not None:
        update_user_role(request.email, request.role)
    
    return {"email": request.email, "credits": user["credits"], "role": user["role"]}


@router.get("/all-users")
async def get_all_users(
    admin_email: str = Depends(require_admin)
):
    """
    Get all users (admin only)
    
    Args:
        admin_email: Admin email (verified by middleware)
    
    Returns:
        All users with their credits and roles
    """
    return {"users": userdict}
