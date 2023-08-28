import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from dundie.app import app
from dundie.cli import create_user

os.environ["DUNDIE_DB__uri"] = "postgresql://postgres:postgres@db:5432/dundie_test"


@pytest.fixture(scope="function")
def api_client():
    """Unauthenticated test client"""
    return TestClient(app)


def create_api_client_authenticated(username, dept="sales", create=True):
    """Creates a new api client authenticated for the specified user."""
    if create:
        try:
            create_user(name=username, email=f"{username}@dm.com", password=username, dept=dept)
        except IntegrityError:
            pass

    client = TestClient(app)
    token = client.post(
        "/token",
        data={"username": username, "password": username},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="function")
def api_client_admin():
    return create_api_client_authenticated("admin", create=False)


@pytest.fixture(scope="function")
def api_client_user1():
    return create_api_client_authenticated("user1", dept="management")


@pytest.fixture(scope="function")
def api_client_user2():
    return create_api_client_authenticated("user2")


@pytest.fixture(scope="function")
def api_client_user3():
    return create_api_client_authenticated("user3")
