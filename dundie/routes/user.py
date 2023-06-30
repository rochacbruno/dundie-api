from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from dundie.auth import AuthenticatedUser, SuperUser
from dundie.db import ActiveSession
from dundie.models.user import User, UserRequest, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse], dependencies=[AuthenticatedUser])
async def list_users(*, session: Session = ActiveSession):
    """List all users."""
    users = session.exec(select(User)).all()
    return users


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(*, session: Session = ActiveSession, username: str):
    """Get single user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    return user


@router.post("/", response_model=UserResponse, status_code=201, dependencies=[SuperUser])
async def create_user(*, session: Session = ActiveSession, user: UserRequest) -> User:
    """Creates a new user"""
    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(status_code=409, detail="User email already exists.")

    db_user = User.from_orm(user)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Database IntegrityError")
    session.refresh(db_user)
    return db_user
