"""ensure_admin_user

Revision ID: 11acfd7547d8
Revises: 1b27082555a1
Create Date: 2023-08-27 22:57:08.179796

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

from dundie.models.user import User
from sqlmodel import Session


# revision identifiers, used by Alembic.
revision = '11acfd7547d8'
down_revision = '1b27082555a1'
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
        password="admin",  # envvar/secrests - colocar password em settings
        currency="USD"
    )

    try:
        session.add(admin)
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()


def downgrade() -> None:
    pass
