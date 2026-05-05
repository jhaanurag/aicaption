"""
Authentication Middleware - validates Bearer tokens and extracts user email
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.services.auth_service import validate_token

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify Bearer token and return email
    
    Args:
        credentials: HTTP Bearer credentials
    
    Returns:
        User email extracted from token
        
    Raises:
        HTTPException: If token invalid or expired
    """
    token = credentials.credentials
    email = validate_token(token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return email


def require_admin(email: str = Depends(verify_token)) -> str:
    """
    Dependency to require admin role
    
    Args:
        email: User email (from verify_token)
    
    Returns:
        Admin email
        
    Raises:
        HTTPException: If user not admin
    """
    from backend.dao.user_dao import get_user
    
    user = get_user(email)
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return email
