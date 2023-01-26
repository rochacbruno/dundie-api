"""ensure_admin_user

Revision ID: 9aa820fb7f01
Revises: 6f4df3b5e155
Create Date: 2023-01-06 13:13:37.907183

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from dundie.models.user import User
from sqlmodel import Session

# revision identifiers, used by Alembic.
revision = '9aa820fb7f01'
down_revision = '6f4df3b5e155'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    admin = User(
        name="Admin",
        username="admin",
        email="admin@dm.com",
        dept="management",
        currency="USD",
        password="admin",  # pyright: ignore
    )
    # if admin user already exists it will raise IntegrityError
    try:
        session.add(admin)
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()


def downgrade() -> None:
    pass
