from fastapi import APIRouter, HTTPException, Request, status
from pymongo.errors import DuplicateKeyError

from backend.dao.user_dao import create_user, list_users, update_user
from backend.middlewares.auth_middleware import admin, get_current_user
from backend.schemas.requests import CreateUserSchema, UpdateUserSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(request: Request):
    return await get_current_user(request)


@router.post("")
async def add_user(data: CreateUserSchema, request: Request):
    await admin(request)
    try:
        return await create_user(data.model_dump(mode="json"))
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")


@router.patch("/{email_id}")
async def edit_user(email_id: str, data: UpdateUserSchema, request: Request):
    await admin(request)
    updates = data.model_dump(exclude_none=True, mode="json")
    updates.pop("email_id", None)
    if "new_email_id" in updates:
        updates["email_id"] = updates.pop("new_email_id")

    user = await update_user(email_id, updates)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{email_id}/deactivate")
async def deactivate_user(email_id: str, request: Request):
    await admin(request)
    user = await update_user(email_id, {"is_active": False})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("")
async def get_all_users(
    request: Request,
    is_active: bool | None = None,
):
    await admin(request)
    return {"users": await list_users(is_active=is_active)}
