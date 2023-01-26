import pytest

USER_RESPONSE_KEYS = {"name", "username", "dept", "avatar", "bio", "currency"}
USER_RESPONSE_WITH_BALANCE_KEYS = USER_RESPONSE_KEYS | {"balance"}


@pytest.mark.order(1)
def test_user_list(
    api_client,
    api_client_user1,  # pyright: ignore
    api_client_user2,  # pyright: ignore
    api_client_user3,  # pyright: ignore
):
    """Ensure that all needed users are created and showing on the /user/ API

    NOTE: user fixtures are called just to trigger creation of users.
    """
    users = api_client.get("/user/").json()
    expected_users = ["admin", "user1", "user2", "user3"]
    assert len(users) == len(expected_users)
    for user in users:
        assert user["username"] in expected_users
        assert user["dept"] in ["management", "sales"]
        assert user["currency"] == "USD"
        assert set(user.keys()) == USER_RESPONSE_KEYS


@pytest.mark.order(2)
def test_user_detail(api_client):
    """Ensure that the /user/{username} API is working"""
    user = api_client.get("/user/user1/").json()
    assert user["username"] == "user1"
    assert set(user.keys()) == USER_RESPONSE_KEYS


@pytest.mark.order(3)
def test_update_user_profile_by_admin(api_client_admin):
    """Ensure that admin can patch any user data"""
    data = {"avatar": "https://example.com/avatar.png", "bio": "I am a user1"}
    api_client_admin.patch("/user/user1/", json=data)
    user = api_client_admin.get("/user/user1/").json()
    assert user["avatar"] == data["avatar"]
    assert user["bio"] == data["bio"]


@pytest.mark.order(3)
def test_update_user_profile_by_user(api_client_user2):
    """Ensure that user can patch their own data"""
    data = {"avatar": "https://example.com/avatar.png", "bio": "I am a user2"}
    api_client_user2.patch("/user/user2/", json=data)
    user = api_client_user2.get("/user/user2/").json()
    assert user["avatar"] == data["avatar"]
    assert user["bio"] == data["bio"]


@pytest.mark.order(3)
def test_fail_update_user_profile_by_other_user(api_client_user2):
    """User 2 will attempt to patch User 1 profile and it will fail"""
    response = api_client_user2.patch("/user/user1/", json={})
    assert response.status_code == 403


@pytest.mark.order(4)
def test_add_transaction_for_users_from_admin(api_client_admin):
    """Admin user adds a transaction for all users"""
    usernames = ["user1", "user2", "user3"]

    for username in usernames:
        api_client_admin.post(f"/transaction/{username}/", json={"value": 500})

    for username in usernames:
        user = api_client_admin.get(f"/user/{username}/?show_balance=true").json()
        assert user["balance"] == 500


@pytest.mark.order(5)
def test_user1_transfer_20_points_to_user2(api_client_user1):
    """Ensure that user1 can transfer points to user2"""
    api_client_user1.post("/transaction/user2/", json={"value": 20})
    user1 = api_client_user1.get("/user/user1/?show_balance=true").json()
    assert user1["balance"] == 480

    # user1 can see balance of user2 because user1 is a manager
    user2 = api_client_user1.get("/user/user2/?show_balance=true").json()
    assert user2["balance"] == 520


@pytest.mark.order(6)
def test_user_list_with_balance(api_client_admin):
    """Ensure that admin can see user balance"""
    users = api_client_admin.get("/user/?show_balance=true").json()
    expected_users = ["admin", "user1", "user2", "user3"]
    assert len(users) == len(expected_users)
    for user in users:
        assert user["username"] in expected_users
        assert set(user.keys()) == USER_RESPONSE_WITH_BALANCE_KEYS


@pytest.mark.order(6)
def test_admin_can_list_all_transactions(api_client_admin):
    """Admin can list all transactions"""
    transactions = api_client_admin.get("/transaction/").json()
    assert transactions["total"] == 4


@pytest.mark.order(6)
def test_regular_user_can_see_only_own_transaction(api_client_user3):
    """Regular user can see only own transactions"""
    transactions = api_client_user3.get("/transaction/").json()
    assert transactions["total"] == 1
    assert transactions["items"][0]["value"] == 500
    assert transactions["items"][0]["user"] == "user3"
    assert transactions["items"][0]["from_user"] == "admin"
