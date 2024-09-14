from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response

from dundie.auth import (
    RefreshToken,
    Token,
    User,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_user,
    validate_token,
)
from dundie.config import settings
from dundie.session import set_session, session_store

ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes  # pyright: ignore
REFRESH_TOKEN_EXPIRE_MINUTES = settings.security.refresh_token_expire_minutes  # pyright: ignore

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(get_user, form_data.username, form_data.password)
    if not user or not isinstance(user, User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    access_token = create_access_token(
        data={"sub": user.username, "fresh": True},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=Token)
async def refresh_token(form_data: RefreshToken):
    user = await validate_token(token=form_data.refresh_token)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    access_token = create_access_token(
        data={"sub": user.username, "fresh": False},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

# session auth

@router.post("/login")
async def session_login(
    response: Response,
    username: str = Form(),
    password: str = Form(),
):
    """Cookie Based Session Auth Login"""
    user = authenticate_user(get_user, username, password)
    if not user or not isinstance(user, User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    session_id = set_session(user.username)
    response.set_cookie(key="session_id", value=session_id, domain="localhost")
    return {"status": "logged in"}


@router.post("/logout")
async def session_logout(request: Request, response: Response):
    """Cookie Based Session Auth Logout"""
    if session_id := request.cookies.get("session_id"):
        response.delete_cookie(key="session_id")
        session_store.delete(session_id)
    return {"status": "logged out"}
