from typing import Optional
from sqlmodel import Session
from dundie.db import engine
from dundie.models import User, Transaction, Balance


class TransactionError(Exception):
    """Can't add transaction"""


def add_transaction(
    *,
    user: User,
    from_user: User,
    value: int,
    session: Optional[Session] = None
):
    """Adds a new transaction to the specified user.

    params:
        user: The user to add transaction to.
        from_user: The user where amount is coming from or superuser
        value: The value being added
    """
    if not from_user.superuser and from_user.balance < value:
        raise TransactionError("Insufficient balance")

    session = session or Session(engine)

    transaction = Transaction(user=user, from_user=from_user, value=value)  # pyright: ignore
    session.add(transaction)
    session.commit()
    session.refresh(user)
    session.refresh(from_user)

    for holder in (user, from_user):
        total_income = sum([t.value for t in holder.incomes])  # pyright: ignore
        total_expense = sum([t.value for t in holder.expenses])  # pyright: ignore
        balance = session.get(
            Balance, holder.id
        ) or Balance(user=holder, value=0)  # pyright: ignore
        balance.value = total_income - total_expense
        session.add(balance)

    session.commit()
