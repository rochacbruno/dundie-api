"""Database connection"""
from fastapi import Depends
from sqlmodel import Session, create_engine

from .config import settings

engine = create_engine(
    settings.db.uri,  # pyright: ignore
    echo=settings.db.echo,  # pyright: ignore
    connect_args=settings.db.connect_args,  # pyright: ignore
)


def get_session():
    with Session(engine) as session:
        yield session


ActiveSession = Depends(get_session)
