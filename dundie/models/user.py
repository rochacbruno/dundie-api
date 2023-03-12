"""User related data models"""
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Represents the User Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: str = Field(nullable=False)
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False)
    currency: str = Field(nullable=False)

    @property
    def superuser(self) -> bool:
        """Users belonging to management dept are admins."""
        return self.dept == "management"
