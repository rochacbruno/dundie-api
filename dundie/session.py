from __future__ import annotations

from uuid import uuid4
from dundie.config import settings
from redis import Redis

EXPIRATION = settings.session_store.get("expiration", 60 * 60 * 24)

session_store = Redis(
    host=settings.session_store.host,
    port=settings.session_store.port,
    db=settings.session_store.db,
)


def set_session(username) -> str:
    """Creates a new random session"""
    session_id = uuid4().hex
    session_store.set(session_id, username, ex=EXPIRATION, nx=True)
    return session_id


def get_session(session_id) -> bool | str:
    """Get data from a session_id"""
    session_data = session_store.get(session_id)
    return session_data and session_data.decode()

