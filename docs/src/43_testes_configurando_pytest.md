# Configurando Pytest

Para os tests vamos utilizar o Pytest para testar algumas rotas da API,
o Pytest pode ser configurado através de hooks e fixtures que ficam no
arquivo `tests/conftest.py`, fixtures são geralmente funções que 
provêm funcionalidades que serão injetadas (via injeção de dependencias)
em cada teste que escrevermos, portanto se queremos testar multiplos
usuários, começamos criando fixtures que preparam clientes HTTP autenticados
com os tokens de cada um desses usuários.

Uma outra coisa importante que faremos é apontar o banco de dados
para o banco de dados de teste que iniciamos no script `test.sh`

# Setup 

01. Obter um token para o usuário admin
00. Criar usuário1
00. Obter um token para o usuário1
00. Criar usuario2
00. Obter um token para o usuario2
00. Criar usuario3
00. Obter um token para o usuario3 

Durante o setup teremos **fixtures** do Pytest já configuradas com clientes
HTTP para acessar a API com qualquer um dos usuários ou de forma anonima.

Começamos configurando o Pytest

**EDITE** `tests/conftest.py`
```python
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
```

Basta salvar o arquivo `conftest.py` e para cada sessão de testes o pytest vai
se certificar que cada uma das fixtures definidas esteja disponível.

```admonish info "INFO"
No treinamento Python Automation é abordado o tema testes e pytest com maior
profundidade, se você quiser saber mais sobre o assunto, recomendo que assista.
```

Agora podemos escrever os testes -->
