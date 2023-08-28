from datetime import datetime
from typing import Optional

from pydantic import BaseModel, root_validator
from sqlmodel import Session

from dundie.db import engine

from .user import User


class TransactionResponse(BaseModel, extra="allow"):
    id: int
    value: int
    date: datetime

    # These 2 fields will be calculated at response time.
    user: Optional[str] = None
    from_user: Optional[str] = None

    @root_validator(pre=True)
    def get_usernames(cls, values: dict):
        with Session(engine) as session:
            user = session.get(User, values["user_id"])
            values["user"] = user and user.username
            from_user = session.get(User, values["from_id"])
            values["from_user"] = from_user and from_user.username
        return values
