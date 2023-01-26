from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.orm import aliased
from sqlmodel import Session, select, text

from dundie.auth import AuthenticatedUser
from dundie.db import ActiveSession
from dundie.models import Transaction, User
from dundie.models.serializers import TransactionResponse
from dundie.tasks.transaction import TransactionError, add_transaction

router = APIRouter()


@router.post('/{username}/', status_code=201)
async def create_transaction(
    *,
    username: str,
    value: int = Body(embed=True),
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
):
    """Adds a new transaction to the specified user."""
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        add_transaction(user=user, from_user=current_user, value=value, session=session)
    except TransactionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # At this point there was no error, so we can return
    return {"message": "Transaction added"}


@router.get("/", response_model=Page[TransactionResponse])
async def list_transactions(
    *,
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
    params: Params = Depends(),
    from_user: Optional[str] = None,
    user: Optional[str] = None,
    order_by: Optional[str] = None,
):
    query = select(Transaction)

    # Optional `AND` filters
    if user:
        query = query.join(User, Transaction.user_id == User.id).where(User.username == user)
    if from_user:
        FromUser = aliased(User)  # aliased needed to desambiguous the join
        query = query.join(FromUser, Transaction.from_id == FromUser.id).where(
            FromUser.username == from_user
        )

    # Mandatory access filter
    # regular users can only see their own transactions
    if not current_user.superuser:
        query = query.where(
            (Transaction.user_id == current_user.id) | (Transaction.from_id == current_user.id)
        )

    # Ordering based on &order_by=date (asc) or -date (desc)
    if order_by:
        order_text = text(order_by.replace("-", "") + " " + ("desc" if "-" in order_by else "asc"))
        query = query.order_by(order_text)

    # wrap response_model in a pagination object {"items": [], total, page, size }
    return paginate(query=query, session=session, params=params)
