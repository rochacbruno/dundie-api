from typing import List

from fastapi import APIRouter, BackgroundTasks, Body
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from dundie.auth import AuthenticatedUser, CanChangeUserPassword, ShowBalanceField, SuperUser
from dundie.queue import queue
from dundie.db import ActiveSession
from dundie.models.user import (
    User,
    UserPasswordPatchRequest,
    UserProfilePatchRequest,
    UserRequest,
    UserResponse,
    UserResponseWithBalance,
)
from dundie.tasks.user import try_to_send_pwd_reset_email

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserResponse] | List[UserResponseWithBalance],
    response_model_exclude_unset=True,
)
async def list_users(
    *, session: Session = ActiveSession, show_balance_field: bool = ShowBalanceField
):
    """List all users.

    NOTES:
    - This endpoint can be accessed with a token authentication
    - show_balance query parameter takes effect only for authenticated superuser.
    """
    users = session.exec(select(User)).all()
    if show_balance_field:
        users_with_balance = parse_obj_as(List[UserResponseWithBalance], users)
        return JSONResponse(jsonable_encoder(users_with_balance))
    return users


@router.get(
    "/{username}/",
    response_model=UserResponse | UserResponseWithBalance,
    response_model_exclude_unset=True,
)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str, show_balance_field: bool = ShowBalanceField
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if show_balance_field:
        user_with_balance = parse_obj_as(UserResponseWithBalance, user)
        return JSONResponse(jsonable_encoder(user_with_balance))
    return user


@router.post("/", response_model=UserResponse, status_code=201, dependencies=[SuperUser])
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Database IntegrityError")

    session.refresh(db_user)
    return db_user


@router.patch("/{username}/", response_model=UserResponse)
async def update_user(
    *,
    session: Session = ActiveSession,
    patch_data: UserProfilePatchRequest,
    current_user: User = AuthenticatedUser,
    username: str,
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # Update
    user.avatar = patch_data.avatar
    user.bio = patch_data.bio

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/{username}/password/", response_model=UserResponse)
async def change_password(
    *,
    session: Session = ActiveSession,
    patch_data: UserPasswordPatchRequest,
    user: User = CanChangeUserPassword,
):
    user.password = patch_data.hashed_password  # pyright: ignore
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/pwd_reset_token/")
async def send_password_reset_token(
    *,
    email: str = Body(embed=True),
    # background_tasks: BackgroundTasks,
):
    # background_tasks.add_task(try_to_send_pwd_reset_email, email=email)
    queue.enqueue(try_to_send_pwd_reset_email, email=email)
    return {"message": "If we found a user with that email, we sent a password reset token to it."}
