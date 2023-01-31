# Testes de API

## Plano de testes

Os casos de uso que iremos testar:

- Como um usuário anonimo consigo listar os usuarios e não posso ver o saldo 
- Como um usuário anonimo consigo listar os detalhes de um usuário sem o saldo 
- Como usuário admin consigo atualizar o perfil de um usuário 
- Como um usuário autenticado consigo atualziar meu próprio perfil 
- Como um usuário autenticado não consigo atualizar o perfil de outro usuário 
- Como usuário admin consigo transferir qualquer quantidade de pontos para todos os usuários
- Como um usuário autenticado consigo tranferir 20 pontos para outro usuário e ver o saldo
- Como um usuário admin consigo ver o saldo de todos os usuários 
- Como um usuário admin consigo ver todas as transações
- Como um usuário autenticado consigo ver apenas minhas transações


## Pytest

Agora vamos converter os casos de uso em funções de teste com o Pytest.

**EDITE** `tests/test_api.py`

```python
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
```

E para executar os tests podemos ir na raiz do projeto **FORA DO CONTAINER**

Garantimos que o script de testes é eecutável.

```console
$ chmod +x test.sh
```

Executamos o script:

```console
$ ./test.sh

[+] Running 3/3
 ⠿ Network dundie-api_default  Created                                                     0.1s
 ⠿ Container dundie-api-db-1   Started                                                     0.7s
 ⠿ Container dundie-api-api-1  Started                                                     1.7s
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running stamp_revision 9aa820fb7f01 -> 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> f39cbdb1efa7, initial
INFO  [alembic.runtime.migration] Running upgrade f39cbdb1efa7 -> b0abf3428204, transaction
INFO  [alembic.runtime.migration] Running upgrade b0abf3428204 -> 9aa820fb7f01, ensure_admin_user
===================================== test session starts ======================================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /home/app/api, configfile: pyproject.toml
plugins: order-1.0.1, anyio-3.6.2
collected 10 items                                                                             

tests/test_api.py::test_user_list PASSED                                                 [ 10%]
tests/test_api.py::test_user_detail PASSED                                               [ 20%]
tests/test_api.py::test_update_user_profile_by_admin PASSED                              [ 30%]
tests/test_api.py::test_update_user_profile_by_user PASSED                               [ 40%]
tests/test_api.py::test_fail_update_user_profile_by_other_user PASSED                    [ 50%]
tests/test_api.py::test_add_transaction_for_users_from_admin PASSED                      [ 60%]
tests/test_api.py::test_user1_transfer_20_points_to_user2 PASSED                         [ 70%]
tests/test_api.py::test_user_list_with_balance PASSED                                    [ 80%]
tests/test_api.py::test_admin_can_list_all_transactions PASSED                           [ 90%]
tests/test_api.py::test_regular_user_can_see_only_own_transaction PASSED                 [100%]

====================================== 10 passed in 4.62s ======================================
[+] Running 3/3
 ⠿ Container dundie-api-api-1  Removed                                                     1.2s
 ⠿ Container dundie-api-db-1   Removed                                                     0.7s
 ⠿ Network dundie-api_default  Removed                                                     0.3s
```

Se tudo deu certo então todos os testes devem ter passado, caso contrário tente encontrar onde
está o erro e corrija antes de prosseguir.

---

Finalizamos assim a fase 1 do nosso projeto com a maior parte das funcionalidades testadas,
vamos partir agora para a fase 2 -> 
