# Projeto Dundie API 

Treinamento Python Web API na https://LINUXtips.io

> **IMPORTANTE**: Este repositório é apenas a estrutura básica para ser usado de template ao iniciar o projeto do treinamento Python Web API na LINUXtips, ao criar seu fork e clonar, a maioria dos arquivos estará vazio propositalmente pois a intenção é que você desenvolva seguindo os passos apresentados no treinamento.

## Requisitos

- Computador com Python 3.10
- Docker & docker-compose
- Ou https://gitpod.io para um ambiente online
- Um editor de códigos como VSCode, Sublime, Vim, Micro
  (Nota: Eu usarei o LunarVim e o Micro)

> **NOTA**: Os comandos apresentados serão executados em um terminal Linux, se estiver no Windows recomendo usar o WSL, uma máquina virtual ou um container Linux, ou por conta própria adaptar os comandos necessários.

## Repositório inicial 

1. Faça login no github e faça um fork do respositório deste projeto clicando em: https://github.com/rochacbruno/dundie-api/fork
2. Clone o projeto para uma pasta no seu ambiente local
  ```
  cd pasta/onde/vc/guarda/seus/projetos
  git clone git@github.com:USER/dundie-api.git
  ```

> **NOTA** para clonar usando `git@` você precisa ter seu git local configurado com chave ssh, caso contrário terá que clonar usando o endereço `https://`


> **DICA** Execute o ambiente online sem precisar instalar nada. 
> Caso não tenha um ambiente local utilize o https://gitpod.io para um ambiente 100% online, faça login no gitpod usando sua conta github.
> Copie a seguinte URL e cole no seu navegador substituindo **USER** pelo seu usuario do github:
> ```
> https://gitpod.io/#https://github.com/USER/dundie-api   
> ```

## Preparando o Ambiente Dev

Primeiro precisamos de um ambiente virtual para instalar
as dependencias do projeto.

```console
python -m venv .venv
```

E ativaremos a virtualenv

```console
# Linux
source .venv/bin/activate
# Windows Power Shell
.\venv\Scripts\activate.ps1
```

Vamos instalar ferramentas de produtividade neste ambiente que estão listadas no arquivo `requirements-dev.txt`

```
ipython         # terminal
ipdb            # debugger
sdb             # debugger remoto
pip-tools       # lock de dependencias
pytest          # execução de testes
pytest-order    # ordenação de testes
httpx           # requests async para testes
black           # auto formatação
flake8          # linter
```

Instalamos as dependencias iniciais.

```console
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e ".[dev]"
```

Estas dependencias estarão disponíveis no ambiente para que você possa utilizar ferramentas de desenvolvimento do seu editor.


## O Projeto

O projeto de chama **dundie** e é uma API para gestão de pontos de recompensa
para funcionários da empresa **Dunder Mifflin**.

<details>

<summary>Clique aqui para ver um Resumo do Projeto</summary>

![Resumo Projeto](images/dundie-api.png)

</details>

## Funcionalidades

### Usuários

- Registro de novos funcionários **via CLI e via API**
  - CLI: `dundie add-user [Nome] [Email] [Departamento] [Password Inicial]`
  - API: `POST /user/ data={nome:.., email:.., departamento:.., password:..}`
  - Cada usuário no momento da criação recebe uma nova transação adicionando 100 pontos
  - Durante o setup do sistema um usuário `admin` será criado com um saldo de 10.000 pontos.
  - Usuários `Manager` recebem 1000 pontos para poder distribuir.
  - O `username` é gerado a partir do slug do nome do usuário `Pam Besly` -> `pam-besly`
- Autenticação de usuários com JWT token
  - Para usar a API será necessário uma chamada `GET /token data={username, password}` e todas as chamadas subsequentes precisarão do token informado nos `HEADERS`. 
- Remoção de usuários via API 
  - Apenas o usuário do departamento `Manager` poderá fazer uma chamada `DELETE /user/username/` e a deleção do usuário será permitida apenas se o saldo de pontos estiver vazio.


Endpoints:
- `POST /user/` cria um novo usuário 
  - Acesso: `Manager`
- `GET /user/username/` retorna os detalhes do usuário
  - Acesso: `Geral`
- `DELETE /user/username/` deleta um usuário
  - Acesso: `Manager`
  - Validação: Saldo zerado


### Transações 

- Transações não podem ser deletadas ou canceladas, cada transação
  é um item no histórico da conta do usuário em questão.
- Qualquer usuário com um token poderá fazer uma chamada para `POST /transaction/username/ data={value=100}` esta chamada adiciona um novo registro na tabela `Transaction` contento `user_id: <usuario_dono_da_conta>, from_id: <usuário que fez o depósito>, value: <integer>, date: <timestamp>`
- O usuário só poderá fazer uma transação caso o saldo da sua própria conta seja suficiente para cobrir o custo da transação.
- O saldo de um usuário é a soma de todas as suas transações.

Endpoints:

- `POST /transaction/username/` - Registra uma transação para um usuário
  - Execução: Task Queue
  - Resposta: `{task_id}`  
  - Acesso: `Geral`
  - Validação: O usuário autenticado é o `from_id` da transação e deve ter saldo suficiente.
- `GET /transaction/username/` - Retorna as transações de um usuário incluindo seu `balance` (saldo todal) 
  - Acesso: `Manager` ou `username == current_user`
- `GET /transaction/` - Retorna todas as transações
  - Acesso: `Manager`
- `GET /transaction/status/{id}/` - Retorna o status de uma transação
  - Response: enum[pending, running, success, failure]
  - Acesso: `Geral`

## Estrutura de pastas e arquivos

Esta é estrutura deste repositório, os arquivos com `*` são os que você vai precisar editar ao longo deste guia.

```
❯ tree --filesfirst -L 3 -I docs
.
├── docker-compose.yaml          # Container Orchestration
├── Dockerfile.dev               # Container Dev Image
├── MANIFEST.in                  # Arquivos do projeto
├── pyproject.toml               # Metadados do projeto
├── requirements-dev.txt         # Dev tools 
├── requirements.in              # Dependencies 
├── settings.toml                # Config por ambiente
├── setup.py                     # Setuptools bootstrap
├── test.sh                      # CI Pipeline 
├── dundie                       # Main Package
│   ├── app.py*                  # FastAPI app
│   ├── auth.py*                 # Token JWT 
│   ├── cli.py*                  # CLI app 
│   ├── config.py                # Config management
│   ├── db.py*                   # Database connection 
│   ├── default.toml             # Default settings 
│   ├── __init__.py
│   ├── security.py*             # Password Hashing
│   ├── VERSION.txt              # SCM versioning
│   ├── models
│   │   ├── __init__.py*
│   │   ├── transaction.py*      # Models for transaction
│   │   └── user.py*             # Models for User
│   ├── routes
│   │    ├── auth.py*             # Token and Auth URLs
│   │    ├── __init__.py*
│   │    ├── transaction.py*      # Transaction URLs 
│   │    └── user.py*             # User URLs 
│   └── tasks
│       ├── __init__.py*
│       ├── transaction.py*      # Transaction Taks 
│       └── user.py*             # User Tasks 
├── postgres
│   ├── create-databases.sh      # DB startup 
│   └── Dockerfile               # DB image 
└── tests
    ├── conftest.py*             # Pytest config 
    ├── __init__.py
    └── test_api.py*             # API tests 
```

## Criando a API base

Vamos editar o arquivo `dundie/app.py`

```python
from fastapi import FastAPI

app = FastAPI(
    title="dundie",
    version="0.1.0",
    description="dundie is a rewards API",
)

```

## Containers

Vamos agora verificar o Dockerfile.dev responsável por executar nossa api

`Dockerfile.dev`

```docker
# Build the app image
FROM python:3.10

# Create directory for the app user
RUN mkdir -p /home/app

# Create the app user
RUN groupadd app && useradd -g app app

# Create the home directory
ENV APP_HOME=/home/app/api
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# install
COPY . $APP_HOME
RUN pip install -r requirements-dev.txt
RUN pip install -e .

RUN chown -R app:app $APP_HOME
USER app

CMD ["uvicorn","dundie.app:app","--host=0.0.0.0","--port=8000","--reload"]

```

Build the container

```bash
docker build -f Dockerfile.dev -t dundie:latest .
```

Execute o container para testar

```console
$ docker run --rm -it -v $(pwd):/home/app/api -p 8000:8000 dundie
INFO:     Will watch for changes in these directories: ['/home/app/api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using StatReload
INFO:     Started server process [8]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Acesse: http://0.0.0.0:8000/docs

![API](images/api_first.png)

## Docker compose

Agora para iniciar a nossa API + o Banco de dados vamos precisar de um
orquestrador de containers, em produção isso será feito com Kubernetes
mas no ambiente de desenvolvimento podemos usar o `docker-compose`.

No arquivo `docker-compose.yaml`

- Definimos 2 serviços `api` e `db`
- Informamos os parametros de build com os dockerfiles
- Na `api` abrimos a porta `8000`
- Na `api` passamos 2 variáveis de ambiente `DUNDIE_DB__uri` e `DUNDIE_DB_connect_args` para usarmos na conexão com o DB
- Marcamos que a `api` depende do `db` para iniciar.
- No `db` informamos o setup básico do postgres e pedimos para criar 2 bancos de dados, um para a app e um para testes.

```yaml
version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      DUNDIE_DB__uri: "postgresql://postgres:postgres@db:5432/${DUNDIE_DB:-dundie}"
      DUNDIE_DB__connect_args: "{}"
    volumes:
      - .:/home/app/api
    depends_on:
      - db
    stdin_open: true
    tty: true
  db:
    build: postgres
    image: dundie_postgres-13-alpine-multi-user
    volumes:
      - $HOME/.postgres/dundie_db/data/postgresql:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DBS=dundie, dundie_test
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
```

O próximo passo é executar com

```bash
docker-compose up -d
```

> **NOTA** Os serviços ficarão em execução em segundo plano, se quiser manter o terminal aberto para acompanhar os logs pode omitir o `-d` ou depois rodar `docker-compose logs --follow`

## Definindo os models com Pydantic

![database](images/database.png)

https://dbdesigner.page.link/GqDU95ApwZs7a9RH9

Vamos modelar o banco de dados definido acima usando o SQLModel, que é
uma biblioteca que integra o SQLAlchemy e o Pydantic e funciona muito bem
com o FastAPI.

Vamos começar a estruturar os model principal para armazenar os usuários

**EDITE** o arquivo `dundie/models/user.py`


```python
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
    def superuser(self):
        return self.dept == "management"
```

**EDITE** arquivo `dundie/models/__init__.py` adicione

```python
from sqlmodel import SQLModel
from .user import User

__all__ = ["User", "SQLModel"]
```

## Settings

Agora que temos pelo menos uma tabela mapeada para uma classe precisamos
estabelecer conexão com o banco de dados e para isso precisamos carregar
configurações

Verifique o arquivo `dundie/default.toml`
```toml
[default]

[default.db]
uri = ""
connect_args = {check_same_thread=false}
echo = false
```

Lembra que no `docker-compose.yaml` passamos as variáveis `DUNDIE_DB...`
aquelas variáveis vão sobrescrever os valores definidos no default
settings.

E a inicialização da biblioteca de configurações:

Veja em `dundie/config.py` como estamos inicializando o plugin de configurações.
```python
"""Settings module"""
import os

from dynaconf import Dynaconf

HERE = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="dundie",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="dundie_env",
    load_dotenv=False,
)
```

No arquivo acima estamos definindo que o objeto `settings` irá
carregar variáveis do arquivo `default.toml` e em seguida dos arquivos
`settings.toml` e `.secrets.toml` e que será possivel usar `DUNDIE_` como
prefixo nas variáveis de ambiente para sobrescrever os valores.


## Conexão com o banco de dados

**EDITE** `dundie/db.py`

```python
"""Database connection"""
from sqlmodel import create_engine
from .config import settings

engine = create_engine(
    settings.db.uri,  # pyright: ignore
    echo=settings.db.echo,  # pyright: ignore
    connect_args=settings.db.connect_args,  # pyright: ignore
)
```

Criamos um objeto `engine` que aponta para uma conexão com o banco de
dados e para isso usamos as variáveis que lemos do `settings`.

## Database Migrations

Portanto agora já temos uma tabela mapeada e um conexão com o banco de dados
precisamos agora garantir que a estrutura da tabela existe dentro do banco
de dados.

Para isso vamos usar a biblioteca `alembic` que gerencia migrações, ou seja,
alterações na estrutura das tabelas.

Começamos na raiz do repositório e rodando:

```bash
alembic init migrations
```

O alembic irá criar um arquivo chamado `alembic.ini` e uma pasta chamada `migrations` que servirá para armazenar o histórico de alterações do banco de dados.

Começaremos editando o arquivo `migrations/env.py`

```py
# No topo do arquivo adicionamos
from dundie import models
from dundie.db import engine
from dundie.config import settings


# Perto da linha 23 mudamos de
# target_metadata = None
# para
target_metadata = models.SQLModel.metadata

# Na função `run_migrations_offline()` mudamos
#  url = config.get_main_option("sqlalchemy.url")
# para
url = settings.db.uri

# Na função `run_migration_online` mudamos
# connectable = engine_from_config...
#para
connectable = engine
```

Agora precisamos fazer só mais um ajuste
edite `migrations/script.py.mako` e em torno da linha 10
adicione

```mako
#from alembic import op
#import sqlalchemy as sa
import sqlmodel  # linha NOVA
```

Agora sim podemos começar a usar o **alembic** para gerenciar as
migrations, precisamos executar este comando dentro do container
portando execute

**IMPORTANTE!!!**: todos os comandos a partir de agora serão executados no shell dentro do container!!!


```console
$ docker-compose exec api /bin/bash
app@c5dd026e8f92:~/api$ # este é o shell dentro do container
```

E dentro do prompt do container rode:

```console
$ alembic revision --autogenerate -m "initial"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
  Generating /home/app/api/migrations/versions/ee59b23815d3_initial.py ...  done
```


> **DICA** alternativamente pode executar `docker-compose exec api COMANDO` ex: `docker-compose exec api python -V`

Repare que o alembic identificou o nosso model `User` e gerou uma migration
inicial que fará a criação desta tabela no banco de dados.

Podemos aplicar a migration rodando dentro do container:

```console
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ee59b23815d3, initial
```

E neste momento a tabela será criada no Postgres, podemos verificar se
está funcionando ainda dentro do container:

**DICA**  
pode usar um client como https://antares-sql.app para se conectar ao banco de dados, usar o psql na linha de comando ou abrir o shell do ipython dentro do container.


```console
# Dentro do shell do container
# alternativa: docker-compose exec api ipython

$ ipython
>>>
```

Digite

```python
from sqlmodel import Session, select
from dundie.db import engine
from dundie.models import User

with Session(engine) as session:
    print(list(session.exec(select(User))))
```

O resultado será uma lista vazia `[]` indicando que ainda não temos nenhum
usuário no banco de dados.

Foi preciso muito **boilerplate** para conseguir se conectar ao banco de dados para facilitar a nossa vida vamos adicionar uma aplicação `cli` onde vamos poder executar tarefas administrativas no shell.

## Criando a CLI base

**EDITE** `dundie/cli.py`

```python


import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from .config import settings
from .db import engine
from .models import User

main = typer.Typer(name="dundie CLI", add_completion=False)


@main.command()
def shell():
    """Opens interactive shell"""
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(
            argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars
        )
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@main.command()
def user_list():
    """Lists all users"""
    table = Table(title="dundie users")
    fields = ["name", "username", "dept", "email", "currency"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(*[getattr(user, field) for field in fields])

    Console().print(table)
```

E agora no shell do container podemos executar

```console
$ docker-compose exec api dundie --help
                                                              
 Usage: dundie [OPTIONS] COMMAND [ARGS]...                    
                                                              
╭─ Options ──────────────────────────────────────────────────╮
│ --help          Show this message and exit.                │
╰────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────╮
│ shell              Opens interactive shell                 │
│ user-list          Lists all users                         │
╰────────────────────────────────────────────────────────────╯
```

E cada um dos comandos:

```console
$ docker-compose exec api dundie user-list
                dundie users                 
┏━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ name ┃ username ┃ dept ┃ email ┃ currency ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
└──────┴──────────┴──────┴───────┴──────────┘
```

e

```console
$ docker-compose exec api dundie shell    
Auto imports: ['settings', 'engine', 'select', 'session', 'User']

In [1]: session.exec(select(User))
Out[1]: <sqlalchemy.engine.result.ScalarResult at 0x7fb539d5e170>

In [2]: settings.db
Out[2]: <Box: {'connect_args': {}, 'uri': 'postgresql://postgres:postgres@db:5432/dundie', 'echo': False}>
```

Ainda não temos usuários cadastrados pois ainda está faltando uma parte importante
**criptografar as senhas** para os usuários.

## Hash passwords


Precisamos ser capazes de encryptar as senhas dos usuários e para isso tem alguns
requisitos, primeiro precisamos de uma chave em nosso arquivo de settings:

**EDITE** `dundie/default.toml` e adicione ao final

```toml
[default.security]
# Set secret key in .secrets.toml
# SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 600
```

Como o próprio comentário acima indica, vamos colocar uma secret key no
arquivo `.secrets.toml` na raiz do repositório.

```toml
[development]
dynaconf_merge = true

[development.security]
# openssl rand -hex 32
SECRET_KEY = "ONLYFORDEVELOPMENT"
```

> NOTA: repare que estamos agora usando a seção `environment` e isso tem a ver
> com o modo como o dynaconf gerencia os settings, esses valores serão
> carregados apenas durante a execução em desenvolvimento.

Você pode gerar uma secret key mais segura se quiser usando
```console
$ python -c "print(__import__('secrets').token_hex(32))"
b9483cc8a0bad1c2fe31e6d9d6a36c4a96ac23859a264b69a0badb4b32c538f8

# OU

$ openssl rand -hex 32
b9483cc8a0bad1c2fe31e6d9d6a36c4a96ac23859a264b69a0badb4b32c538f8
```

**EDITE** Agora vamos o `dundie/security.py` e adicione alguns elementos

```python
"""Security utilities"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    """Verifies a hash against a password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Generates a hash from plain text"""
    return pwd_context.hash(password)


class HashedPassword(str):
    """Takes a plain text password and hashes it.
    use this as a field in your SQLModel
    class User(SQLModel, table=True):
        username: str
        password: HashedPassword
    """

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Accepts a plain text password and returns a hashed password."""
        if not isinstance(v, str):
            raise TypeError("string required")

        hashed_password = get_password_hash(v)
        # you could also return a string here which would mean model.password
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return cls(hashed_password)
```

**EDITE** agora o arquivo `dundie/models/user.py`

No topo na linha 4

```python
from dundie.security import HashedPassword
```

E no model mudamos o campo `password` na linha 18 para

```python
password: HashedPassword
```

E no final de `models/user.py` uma função para gerar os usernames 

```python 
def generate_username(name: str) -> str:
    """Generates a slug username from a name"""
    return name.lower().replace(" ", "-")
```
 
 
 
 
## Adicionando usuários pelo cli

**EDITE** `dundie/cli.py` e adicione 

```python 
from dundie.models.user import generate_username
```


e no final adicione
```python
@main.command()
def create_user(
    name: str,
    email: str,
    password: str,
    dept: str,
    username: str | None = None,
    currency: str = "USD",
):
    """Create user"""
    with Session(engine) as session:
        user = User(
            name=name,
            email=email,
            password=password,  # pyright: ignore
            dept=dept,
            username=username or generate_username(name),
            currency=currency,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {user.username} user")
        return user
```

E no terminal do container execute

```console
❯ docker-compose exec api dundie create-user --help
                                                    
 Usage: dundie create-user [OPTIONS] NAME EMAIL     
                           PASSWORD DEPT            
                                                    
 Create user                                        
                                                    
╭─ Arguments ──────────────────────────────────────╮
│ *    name          TEXT  [default: None]         │
│                          [required]              │
│ *    email         TEXT  [default: None]         │
│                          [required]              │
│ *    password      TEXT  [default: None]         │
│                          [required]              │
│ *    dept          TEXT  [default: None]         │
│                          [required]              │
╰──────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────╮
│ --username        TEXT  [default: None]          │
│ --currency        TEXT  [default: USD]           │
│ --help                  Show this message and    │
│                         exit.                    │
╰──────────────────────────────────────────────────╯
```

E então

```console
$ docker-compose exec api dundie create-user \     
    "Michael Scott" mscott@dm.com boss123 management 
created michael-scott user

$ docker-compose exec api dundie user-list
                              dundie users                               
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ name          ┃ username      ┃ dept       ┃ email         ┃ currency ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Michael Scott │ michael-scott │ management │ mscott@dm.com │ USD      │
└───────────────┴───────────────┴────────────┴───────────────┴──────────┘
```

Agora vamos para a API

## Adicionando rotas de usuários


Agora vamos criar endpoints na API para efetuar as operações que fizemos
através da CLI, teremos as seguintes rotas:

- `GET /user/` - Lista todos os usuários
- `POST /user/` - Cadastro de novo usuário
- `GET /user/{username}/` - Detalhe de um usuário

> **TODO:** A exclusão de usuários será implementada depois.

### Serializers

A primeira coisa que precisamos é definir serializers, que são models
intermediários usados para serializar e de-serializar dados de entrada e saída
da API e eles são necessários pois não queremos export o model do
banco de dados diretamente na API.

**EDITE** `dundie/models/user.py`

No topo na linha 5

```python
from pydantic import BaseModel, root_validator
```

No final após a linha 20

```python
class UserResponse(BaseModel):
    """Serializer for User Response"""

    name: str
    username: str
    dept: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    currency: str


class UserRequest(BaseModel):
    """Serializer for User request payload"""

    name: str
    email: str
    dept: str
    password: str
    currency: str = "USD"
    username: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

    @root_validator(pre=True)
    def generate_username_if_not_set(cls, values):
        """Generates username if not set"""
        if values.get("username") is None:
            values["username"] = generate_username(values["name"])
        return values
```

Podemos testar os serializers em nosso shell.

```python
$ docker-compose exec api dundie shell    
Auto imports: ['settings', 'engine', 'select', 'session', 'User']

In [1]: from dundie.models.user import UserRequest

In [2]: new = UserRequest(
   ...:     name="Bruno Rocha",
   ...:     email="bruno@dm.com",
   ...:     dept="Sales",
   ...:     password="1234",
   ...:  )

In [3]: new.username
Out[3]: 'bruno-rocha'

In [4]: new.currency
Out[4]: 'USD'

In [5]: db_user = User.from_orm(new)

In [6]: session.add(db_user)

In [7]: session.commit()


In [12]: session.exec(select(User).where(User.username=="bruno-rocha")).first()

Out[12]: User(bio=None, email='bruno@dm.com', username='bruno-rocha', name='Bruno Rocha', currency=
'USD', id=2, avatar=None, password='$2b$12$v/1h3sKAFCOuiKuXsThAXOBuny46TPYzKyoaBVisCFHlwaxPlKWpu', 
dept='Sales')

```

Como pode ver acima podes criar usuários via API e serializar usando o `UserRequest` e só a partir dele criar a instancia de `User`  que iremos salvar no banco de dados.  

E da mesma forma podemos fazer o caminho inverso, serializando do banco de dados para a API em JSON.

```python
In [19]: bruno = session.exec(select(User).where(User.username=="bruno-rocha")).first()

In [20]: from dundie.models.user import UserResponse

In [21]: UserResponse.parse_obj(bruno).json()
Out[21]: '{"name": "Bruno Rocha", "username": "bruno-rocha", "dept": "Sales", "avatar": null, "bio"
: null, "currency": "USD"}'
```

E agora criaremos as URLS para expor esses serializers com os usuários
edite `dundie/routes/user.py`

```python
from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from dundie.db import ActiveSession
from dundie.models.user import User, UserRequest, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(*, session: Session = ActiveSession):
    """List all users."""
    users = session.exec(select(User)).all()
    return users


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```

Agora repare que estamos importando `ActiveSession` mas este objeto não existe
em `dundie/db.py` então vamos criar


No topo de `dundie/db.py` nas linhas 2 e 3
```python
from fastapi import Depends
from sqlmodel import Session, create_engine
```

No final de `dundie/db.py` após a linha 13

```python
def get_session():
    with Session(engine) as session:
        yield session


ActiveSession = Depends(get_session)
```

O objeto que `ActiveSession` é uma dependência para rotas do FastAPI
quando usarmos este objeto como parâmetro de uma view o FastAPI
vai executar de forma **lazy** este objeto e passar o retorno da função
atrelada a ele como argumento da nossa view.

Neste caso teremos sempre uma conexão com o banco de dados dentro de cada
view que marcarmos com `session: Session = ActiveSession`.

Agora podemos mapear as rotas na aplicação principal primeiro criamos um
router principal que serve para agregar todas as rotas:

em `dundie/router/__init__.py`

```python
from fastapi import APIRouter

from .user import router as user_router

main_router = APIRouter()

main_router.include_router(user_router, prefix="/user", tags=["user"])
```

E agora em `dundie/app.py`

NO topo na linha 4
```python
from .routes import main_router
```

Logo depois de `app = FastAPI(...` após a linha 11
```python
app.include_router(main_router)
```

E agora sim pode acessar a API e verá as novas rotas prontas para serem usadas,
http://0.0.0.0:8000/docs/

![user routes](images/user_routes1.png)

Pode tentar pela web interface ou com um http client puro:

```http
# rest_nvim
GET http://localhost:8000/user/
#+END
HTTP/1.1 200 OK
date: Fri, 23 Dec 2022 18:04:23 GMT
server: uvicorn
content-length: 220
content-type: application/json

#+RESPONSE
[
  {
    "name": "Michael Scott",
    "username": "michael-scott",
    "dept": "management",
    "avatar": null,
    "bio": null,
    "currency": "USD"
  },
  {
    "name": "Bruno Rocha",
    "username": "bruno-rocha",
    "dept": "Sales",
    "avatar": null,
    "bio": null,
    "currency": "USD"
  }
]
#+END
```

Ou diretamente via cURL


```bash
curl -X 'GET' -k 'http://localhost:8000/user/'
```

Ou criar um usuário

```bash
curl -X 'POST' -H 'Content-Type: application/json' \
  --data-raw '{"email": "pam@dm.com", "dept": "Accounting", "password": "jimjim", "name": "Pam Besly"}' \
  -k 'http://localhost:8000/user/'
```

Pegar um usuário pelo username

```bash
curl -X 'GET' -k 'http://localhost:8000/user/michael-scott/'
```
```json
{
  "name": "Michael Scott",
  "username": "michael-scott",
  "dept": "management",
  "avatar": null,
  "bio": null,
  "currency": "USD"
}
```

Listar todos

```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/user/' \
  -H 'accept: application/json'
```
```json
[
  {
    "name": "Michael Scott",
    "username": "michael-scott",
    "dept": "management",
    "avatar": null,
    "bio": null,
    "currency": "USD"
  },
  {
    "name": "Bruno Rocha",
    "username": "bruno-rocha",
    "dept": "Sales",
    "avatar": null,
    "bio": null,
    "currency": "USD"
  },
  {
    "name": "Dwight Schrute",
    "username": "dwight-schrute",
    "dept": "Sales",
    "avatar": null,
    "bio": null,
    "currency": "USD"
  },
  {
    "name": "Pam Besly",
    "username": "pam-besly",
    "dept": "Accounting",
    "avatar": null,
    "bio": null,
    "currency": "USD"
  },
  {
    "name": "Jim Halpert",
    "username": "jim-halpert",
    "dept": "Sales",
    "avatar": null,
    "bio": null,
    "currency": "USD"
  }
]
```

## Autenticação

Agora que já podemos criar usuários é importante conseguirmos autenticar
os usuários pois desta forma podemos começar a criar postagens via API

Esse será arquivo com a maior quantidade de código **boilerplate**.

**EDITE** o arquivo `dundie/auth.py` vamos criar as classes e funções necessárias
para a implementação de JWT que é a autenticação baseada em token e vamos
usar o algoritmo selecionado no arquivo de configuração.

`dundie/auth.py`
```python
"""Token based auth"""
from datetime import datetime, timedelta
from typing import Callable, Optional, Union
from functools import partial

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from dundie.config import settings
from dundie.db import engine
from dundie.models.user import User
from dundie.security import verify_password

SECRET_KEY = settings.security.secret_key  # pyright: ignore
ALGORITHM = settings.security.algorithm  # pyright: ignore


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Models


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Functions


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    scope: str = "access_token",
) -> str:
    """Creates a JWT Token from user data

    scope: access_token or refresh_token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "scope": scope})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,  # pyright: ignore
        algorithm=ALGORITHM,  # pyright: ignore
    )
    return encoded_jwt


create_refresh_token = partial(create_access_token, scope="refresh_token")


def authenticate_user(
    get_user: Callable, username: str, password: str
) -> Union[User, bool]:
    """Authenticate the user"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user(username) -> Optional[User]:
    """Get user from database"""
    query = select(User).where(User.username == username)
    with Session(engine) as session:
        return session.exec(query).first()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    request: Request = None,  # pyright: ignore
    fresh=False
) -> User:
    """Get current user authenticated"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if request:
        if authorization := request.headers.get("authorization"):
            try:
                token = authorization.split(" ")[1]
            except IndexError:
                raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,  # pyright: ignore
            algorithms=[ALGORITHM]  # pyright: ignore
        )
        username: str = payload.get("sub")  # pyright: ignore

        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    if fresh and (not payload["fresh"] and not user.superuser):
        raise credentials_exception

    return user


# FastAPI dependencies

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Wraps the sync get_active_user for sync calls"""
    return current_user


AuthenticatedUser = Depends(get_current_active_user)


async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    """Validates user token"""
    user = get_current_user(token=token)
    return user
```

> **NOTA**: O objeto `AuthenticatedUser` é uma dependência do FastAPI e é
> através dele que iremos garantir que nossas rotas estejas protegidas
> com token.

A simples presença das urls `/token` e `/refresh_token` fará o FastAPI
incluir autenticação na API portanto vamos definir essas urls:

**EDITE** `dundie/routes/auth.py`
```python
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from dundie.auth import (
    RefreshToken,
    Token,
    User,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_user,
    validate_token,
)
from dundie.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes  # pyright: ignore
REFRESH_TOKEN_EXPIRE_MINUTES = settings.security.refresh_token_expire_minutes  # pyright: ignore

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(get_user, form_data.username, form_data.password)
    if not user or not isinstance(user, User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    access_token = create_access_token(
        data={"sub": user.username, "fresh": True},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=Token)
async def refresh_token(form_data: RefreshToken):
    user = await validate_token(token=form_data.refresh_token)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    access_token = create_access_token(
        data={"sub": user.username, "fresh": False},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)  # pyright: ignore
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
```

E agora vamos adicionar essas URLS ao router principal

`dundie/routes/__init__.py`

No topo na linha 3

```python
from .auth import router as auth_router
```

E depois na linha 9

```python
main_router.include_router(auth_router, tags=["auth"])
```

Vamos testar a aquisição de um token via curl ou através da UI.

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=michael-scott&password=boss123'
```


```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImZyZXNoIjp0cnVlLCJleHAiOjE2Njg2Mjg0NjgsInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0.P-F3onD2vFFIld_ls1irE9rOgLNk17SNDASls31lgkU",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY2ODY2MjY2OCwic2NvcGUiOiJyZWZyZXNoX3Rva2VuIn0.AWV8QtySYmcukxTgTa9GedLK00o6wrbyMt9opW42eyQ",
  "token_type": "bearer"
}
```

## Protegendo com autenticação

Apenas super usuários terão permissão para criar novos usuários, portanto
vamos proteger a view `POST /user/` com autenticação via **TOKEN**


**EDITE** `dundie/auth.py` e adicione no final uma dependencia para 
garantir que o usuário autenticado é super usuário.

```python
async def get_current_super_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a super user"
        )
    return current_user


SuperUser = Depends(get_current_super_user)
```

Agora vamos usar essa dependencia para garantir o super usuário em nossa rota 
**EDITE** `dundie/routes/user.py`  

No topo próximo a linha 9

```python
from dundie.auth import SuperUser
```

E no roteamento da view `create_user` no final 

```python

@router.post("/", response_model=UserResponse, status_code=201, dependencies=[SuperUser])
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    ...

```

Adicionamos `dependencies=[SuperUser]` no roteamento e isso é o suficiente para o FastAPI detectar que existe pelo menos uma URL que necessita de autenticação e agora já teremos os controles de autenticação na API.

![Auth](images/auth_form.png)


Ao tentar criar um usuário sem autenticar teremos agora um erro `HTTP_401_UNAUTHORIZED` e se o usuário autenticado não for um superuser termos o erro `HTTP_403_FORBIDDEN`


Os requests vão precisar do token, portanto o usuário primeiro precisa pedir um token na URL `/token` e depois usar este token na requisição protegida 

```bash
curl -X 'POST' \
  'http://localhost:8000/user/?fresh=false' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsLXNjb3R0IiwiZnJlc2giOnRydWUsImV4cCI6MTY3MTgyOTc2NCwic2NvcGUiOiJhY2Nlc3NfdG9rZW4ifQ.wdIUyJS9TX2Ku8BMI_AIJhAXQb-TSHmX11qKs5C4PF0' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Kevin Malone",
  "email": "kevin@dm.com",
  "dept": "Sales",
  "password": "stacy"
}'

```


## Tratando erros 

Agora vamos tentar duplicar a criação de um usuário fazendo novamente a mesma chamada POST e a mensagem que receberemos é:

```http
HTTP/1.1 500 Internal Server Error

Internal Server Error
```

A mensagem de erro não ajuda muito a sabermos o que ocorreu de fato e portanto podemos curtomizar este comportamento.

Quando temos este caso expecifico o código de erro correto é o `409 Conflict` que innforma que o estado interno está em conflito com o estado que está sendo enviado no request.

Para customizar este comportamento podemos editar o arquivo `routes/user.py`

```python
# No topo
from sqlalchemy.exc import IntegrityError

# Na função `create_user`
async def create_user(.......):
    ...
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists")
```

A exception `IntegrityError` será levantada para qualquer problemas encontrado no banco de dados portanto não é ainda a melhor opção, precisamos ser mais especificos para ajudar quem está usando a API, portanto vamos fazer as seguintes modificações:

1. Continuar tratando a IntegrityError porém com o código 500 e mensagem de erro genérica.
2. Adicionar um guard para garantir que o usuário não existe.


```python
@router.post("/", response_model=UserResponse, status_code=201, dependencies=[SuperUser])
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Database IntegrityError")

    session.refresh(db_user)
    return db_user
```

E agora sim teremos o retorno esperado 

```http
HTTP/1.1 409 Conflict
```

E no caso de um outro erro de integridade ai invés de mostrar apenas o erro 500 gnérico informamos especificamente que se trata de um problema no banco de dados, porém sem expor o erro diretamente.

> **NOTA** Uma boa prática seria colocar um logger ou um analisador de exceptions como o NewRElic.


<!-- TODO:  

0. Permitir que o usuário edite o perfil
1. Permitir que o usuário altere a senha
2. Permitir que o manager altere a senha
3. Permitir que o usuário peça um email
    de alteração de senha

-->


## Update profile 

Agora vamos adicionar uma rota para que o usuário possa alterar o próprio perfil.

O usuário será capaz de mudar apenas os campos `bio` e `avatar`  
bio será um texto e avatar a URL de uma imagem.

Vamos começar criando o serializer que irá receber essas informações:

**EDITE** `models/user.py`

```python
class UserProfilePatchRequest(BaseModel):
    avatar: Optional[str] = None
    bio: Optional[str] = None
```

E agora adicionamos a URL em `routes/user.py`

```python

@router.patch("/{username}/", response_model=UserResponse)
async def update_user(
    *,
    session: Session = ActiveSession,
    patch_data: UserProfilePatchRequest,
    current_user: User = AuthenticatedUser,
    username: str
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # Update
    user.avatar = patch_data.avatar
    user.bio = patch_data.bio

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

```bash
curl -X 'PATCH' \
 -H 'Authorization: Bearer ...' \
 -H 'Content-Type: application/json' 
 --data-raw '{"avatar": "https://test.com/MichaelScott.png", "bio": "I am the boss"}' \
 -k 'http://localhost:8000/user/michael-scott/'
```


## Update de senha

O endpoint de alteração de senha precisa ficar separado do perfil
pois este endpoint precisa de alguns detalhes extras:

01. O usuário precisa preencher a senha e a confirmação 
00. A mudança pode ser feita pelo próprio usuário, pelo superuser ou através de um token requisitado por email (esqueci a senha)

Começamos adicionando o serializer para receber o request da alteração do password.

**EDITE** `models/user.py`
```python

from fastapi import HTTPException, status
from dundie.security import get_password_hash

...


class UserPasswordPatchRequest(BaseModel):
    password: str
    password_confirm: str

    @root_validator(pre=True)
    def check_passwords_match(cls, values):
        """Checks if passwords match"""
        if values.get("password") != values.get("password_confirm"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        return values

    @property
    def hashed_password(self) -> str:
        """Returns hashed password"""
        return get_password_hash(self.password)
```

Para editar o password do usuário teremos as seguintes condições 

```python
current_user == user
# OR
current_user.supersuser is True
# OR
Query.token.is_valid
```

Vamos implementar a lógica acima como uma dependencia do FastAPI

**EDITE** `dundie/auth.py` e no final:
```python
async def get_user_if_change_password_is_allowed(
    *,
    request: Request,
    pwd_reset_token: Optional[str] = None,  # from path?pwd_reset_token=xxxx
    username: str,  # from /path/{username}
) -> User:
    """Returns User if one of the conditions is met.
    1. There is a pwd_reset_token passed as query parameter and it is valid OR
    2. authenticated_user is supersuser OR
    3. authenticated_user is User
    """
    target_user = get_user(username)  # The user we want to change the password
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        valid_pwd_reset_token = get_current_user(token=pwd_reset_token or "") == target_user
    except HTTPException:
        valid_pwd_reset_token = False

    try:
        authenticated_user = get_current_user(token="", request=request)
    except HTTPException:
        authenticated_user = None

    if any(
        [
            valid_pwd_reset_token,
            authenticated_user and authenticated_user.superuser,
            authenticated_user and authenticated_user.id == target_user.id,
        ]
    ):
        return target_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to change this user's password",
    )


CanChangeUserPassword = Depends(get_user_if_change_password_is_allowed)
```

Agora temos `CanChangeUserPassword` como dependencia para usar em uma rota do FastAPI
isso vai garantir que a URL só será executada se todas as condições da dependencia foram
resolvidas.

E agora em `routes/user.py` vamos criar uma rota com o método `POST`

> **NOTA** o ideal para seguir a semantica REST seria criar este método como **PATCH** porém formulários HTML permitem apenas GET e POST e para facilitar o trabalho do front-end vamos usar POST.

```python
@router.post("/{username}/password/", response_model=UserResponse)
async def change_password(
    *,
    session: Session = ActiveSession,
    patch_data: UserPasswordPatchRequest,
    user: User = CanChangeUserPassword
):
    user.password = patch_data.hashed_password  # pyright: ignore
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

## Esqueci a senha

O próximo passo para completar a gestão de usuários é criarmos uma URL onde o usuário irá informar o seu `email` e o sistema vai verificar se existe um usuário com este e-mail cadastrado e então enviar um e-mail com o token para permitir a alteração de senha.

Nós já temos uma função que é capaz de gerar um token em `dundie/auth.py` chamada `create_access_token`

E vamos usar esta função para gerar o token de alteração de senha.

O fluxo será o seguinte:

01. Usuário requisita um token de senha em 

```http
POST /user/pwd_reset_token/

{
  "email": "michael-scott@dm.com"
}
```
```
Response: 200 Ok
"Email will be sent if user is registered"
```

02. A view responsável por `/user/pwd_reset_token`
vai fazer o seguinte:

- Produzir uma background task `try_to_send_pwd_reset_email(email)`.

03. A função `try_to_send_pwd_reset_email` será uma task iniciada em background e irá fazer o seguinte:

1. Procurar o usuário pelo e-mail
2. Criar um token com expiração curta (Settings)
3. Renderizar um template com o link para redefinir senha (Settings)
4. Enviar o e-mail

## Background tasks

O FastAPI já tem suporte a background tasks, assim que o usuário requisita o link para resetar o password, ao invés dele ficar esperando a resposta, nós criamos uma background task que vai executar asincronamente na mesma thread porém liberando a resposta do request.

> **NOTA** para processamento mais intensivo será recomendado utilizar um serviço dedicado a task queue o Celery ou o RQ, para tarefas simples como envio de email podemos fazer com asyncio.

Vamos começar criando uma função que irá receber alguns parametros e enviar um e-mail.

**EDITE** `dundie/tasks/user.py`

```python
import smtplib
from datetime import timedelta
from time import sleep

from sqlmodel import Session, select

from dundie.auth import create_access_token
from dundie.config import settings
from dundie.db import engine
from dundie.models.user import User


def send_email(email: str, message: str):
    if settings.email.debug_mode is True:  # pyright: ignore
        _send_email_debug(email, message)
    else:
        _send_email_smtp(email, message)


def _send_email_debug(email: str, message: str):
    """Mock email sending by printing to a file"""
    with open("email.log", "a") as f:
        sleep(3)  # pretend it takes 3 seconds
        f.write(f"--- START EMAIL {email} ---\n" f"{message}\n" "--- END OF EMAIL ---\n")


def _send_email_smtp(email: str, message: str):
    """Connect to SMTP server and send email"""
    with smtplib.SMTP_SSL(
        settings.email.smtp_server, settings.email.smtp_port  # pyright: ignore  # pyright: ignore
    ) as server:
        server.login(settings.email.smtp_user, settings.email.smtp_password)  # pyright: ignore
        server.sendmail(
            settings.email.smtp_sender,  # pyright: ignore
            email,
            message.encode("utf8"),
        )


MESSAGE = """\
From: Dundie <{sender}>
To: {to}
Subject: Password reset for Dundie

Please use the following link to reset your password:
{url}?pwd_reset_token={pwd_reset_token}

This link will expire in {expire} minutes.
"""
# TODO: The message can be moved to an external template


def try_to_send_pwd_reset_email(email):
    """Given an email address sends email if user is found"""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            return

        sender = settings.email.smtp_sender  # pyright: ignore
        url = settings.security.PWD_RESET_URL  # pyright: ignore
        expire = settings.security.RESET_TOKEN_EXPIRE_MINUTES  # pyright: ignore

        pwd_reset_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=expire),  # pyright: ignore
            scope="pwd_reset",
        )

        send_email(
            email=user.email,
            message=MESSAGE.format(
                sender=sender,
                to=user.email,
                url=url,
                pwd_reset_token=pwd_reset_token,
                expire=expire,
            ),
        )

```

O próximo passo é editar o arquivo `dundie/default.toml` e adicionar os settings necessários para o serviço de emails.

```toml
[default.security]
...
RESET_TOKEN_EXPIRE_MINUTES = 10
PWD_RESET_URL = "https://dm.com/reset_password"

[default.email]
debug_mode = true
smtp_sender = "no-reply@dm.com"
smtp_server = "localhost"
smtp_port = 1025
smtp_user = "<replace in .secrets.toml>"
smtp_password = "<replace in .secrets.toml>"
```

Agora podemos abrir um terminal e testar essas funções

```bash
❯ docker-compose exec api dundie shell
Auto imports: ['settings', 'engine', 'select', 'session', 'User']

In [1]: from dundie.tasks.user import try_to_send_pwd_reset_email

In [2]: try_to_send_pwd_reset_email("mscott@dm.com")

In [3]: open("email.log").readlines()
Out[3]: 
['--- START EMAIL mscott@dm.com ---\n',
 'From: Dundie <no-reply@dm.com>\n',
 'To: mscott@dm.com\n',
 'Subject: Password reset for Dundie\n',
 '\n',
 'Please use the following link to reset your password:\n',
 'https://dm.com/reset_password?pwd_reset_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsLXNjb3R0IiwiZXhwIjoxNjcyNjc3OTk1LCJzY29wZSI6InB3ZF9yZXNldCJ9.nAZNxHYniofTSCzBh38gPi5Qd0FoKONw1Ge6Yp40l5s\n',
 '\n',
 'This link will expire in 10 minutes.\n',
 '\n',
 '--- END OF EMAIL ---\n']
```

Cada e-mail enviado será adicionado ao arquivo email.log enquanto `settings.email.debug_mode` estiver ativado, futuramente podemos colocar os dados de um servidor smtp de verdade.

Agora a parte principal é criar uma rota que permitirá ao iusuário solicitar o token de alteração de senha e disparar a task em background para o envio do e-mail.

**EDITE** `dundie/routes/user.py` e no final vamos adicionar.


```python
from dundie.tasks.user import try_to_send_pwd_reset_email


@router.post("/pwd_reset_token/")
async def send_password_reset_token(*, email: str = Body(embed=True)):
    try_to_send_pwd_reset_email(email)
    return {
        "message": "If we found a user with that email, we sent a password reset token to it."
    }
```

Testando:

```bash
curl -X 'POST' -H 'Content-Type: application/json' \
--data-raw '{"email": "mscott@dm.com"}' -k \
'http://localhost:8000/user/pwd_reset_token/'
```

```http
POST http://localhost:8000/user/pwd_reset_token/
#+END
HTTP/1.1 200 OK
date: Mon, 02 Jan 2023 16:42:56 GMT
server: uvicorn
content-length: 87
content-type: application/json

#+RESPONSE
{
  "message": "If we found a user with that email, we sent a password reset token to it."
}
#+END
```

> **NOTA** por questões de privacidade nós não podemos confirmar se a operação deu certo.


**Mas e as background tasks???**

Ao chamar a URL `/user/pwd_reset_token/` a resposta demorou 3 segundos pois estamos bloqueando o request até o e-mail ser enviado, o ideal é que isso seja feito em background, vamos transformar a chamada de `try_to_send_pwd_reset_email` em uma task.


**EDITE** `dundie/routes/user.py`

```python
from fastpi import BackgroundTasks
...


@router.post("/pwd_reset_token/")
async def send_password_reset_token(
    *,
    email: str = Body(embed=True),
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(try_to_send_pwd_reset_email, email=email)
    return {
        "message": "If we found a user with that email, we sent a password reset token to it."
    }
```

Assim terminamos a API de gestão de usuários e Auth por enquanto

![](images/user_final.png)

Com estas rotas agora já podemos ter um front-end integrado para a gestão de usuários, mas o nosso próximo passo é cuidar da API de transações.


## API de Transações

A modelagem dos dados é a seguinte

![database](images/database.png)

https://dbdesigner.page.link/GqDU95ApwZs7a9RH9

Portanto criaremos os models para `Transaction` e `Balance`

**EDITE** `dundie/models/transaction.py`

```python
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from dundie.models.user import User


class Transaction(SQLModel, table=True):
    """Represents the Transaction Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    from_id: int = Field(foreign_key="user.id", nullable=False)
    value: int = Field(nullable=False)
    date: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Populates a `.incomes` on `User`
    user: Optional["User"] = Relationship(
        back_populates="incomes",
        sa_relationship_kwargs={"primaryjoin": 'Transaction.user_id == User.id'},
    )
    # Populates a `.expenses` on `User`
    from_user: Optional["User"] = Relationship(
        back_populates="expenses",
        sa_relationship_kwargs={"primaryjoin": 'Transaction.from_id == User.id'},
    )


class Balance(SQLModel, table=True):
    """Store the balance of a user account"""

    user_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        primary_key=True,
        unique=True,
    )
    value: int = Field(nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # Populates a `._balance` on `User`
    user: Optional["User"] = Relationship(back_populates="_balance")
```

E as respectivas mudanças ao `dundie/models/user.py`

```python
from typing import TYPE_CHECKING, Optional


class User(...):
    ...

    # Populates a `.user` on `Transaction`
    incomes: Optional[list["Transaction"]] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"primaryjoin": 'User.id == Transaction.user_id'},
    )
    # Populates a `.from_user` on `Transaction`
    expenses: Optional[list["Transaction"]] = Relationship(
        back_populates="from_user",
        sa_relationship_kwargs={"primaryjoin": 'User.id == Transaction.from_id'},
    )
    # Populates a `.user` on `Balance`
    _balance: Optional["Balance"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic"}
    )

    @property
    def balance(self) -> int:
        """Returns the current balance of the user"""
        if (user_balance := self._balance.first()) is not None:  # pyright: ignore
            return user_balance.value
        return 0
```

E por fim adicionamos o novo model ao contexto do `dundie/models/__init__.py`

```python
from sqlmodel import SQLModel
from .user import User
from .transaction import Transaction, Balance

__all__ = ["User", "SQLModel", "Transaction", "Balance"]
```

Com os models criados pediamos ao **alembic** para criar o arquivo de migration

```console
$ docker-compose exec api alembic revision --autogenerate -m "transaction"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.

INFO  [alembic.autogenerate.compare] Detected added table 'balance'
INFO  [alembic.autogenerate.compare] Detected added table 'transaction'

INFO  [alembic.ddl.postgresql] Detected sequence named 'user_id_seq' as owned by integer column 'user(id)', assuming SERIAL and omitting
  Generating /home/app/api/migrations/versions/8af1cd3be673_transaction.py ...  done
```

E em sequencia aplicamos para criar as tabelas no banco de dados:

```console
❯ docker-compose exec api alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade f39cbdb1efa7 -> b0abf3428204, transaction
```

Neste momento nossas tabelas `transaction` e `balance` já devem estar criadas.

**Antares SQL**
![](images/antares_transaction.png)


## Adicionando transactions

A operação de adicionar uma transação será feita com uma requisiçãp `POST` ao endpoint `/transaction/`
e o corpo da transaction será:

```json
{
  "user_id": "integer",
  "value": "integer",
}
```

O usuário autenticado através de token será usado para popular o campo `from_id` e o campo `date` será
preenchido automaticamente.

> **NOTE** Via `CLI` também será possivel adicionar transaction, e neste caso o `from_id` será o user `admin` (que precisamos garantir a criação via migrations)

### Checagens

- A operação de transaction deve:  
    01. Obter os usuários 
    00. Iniciar uma database-transaction
    00. Procedimento permitido? 
        01. from_id.saldo >= value OR from_id.uperuser
            01. Criar `Transaction`
            00. Atualizar os saldos de `user_id` e `from_id`
            00. Dar commit na session
        00. saldo < value 
            01. Retornar com erro


### Atualizando Saldo

Vamos criar uma função com a lógica necessária para adicionar transaction e atualizar
o saldo baseando-se nas regras anteriores.

**EDITE** `dundie/tasks/transaction.py`

```python
from typing import Optional
from sqlmodel import Session
from dundie.db import engine
from dundie.models import User, Transaction, Balance


class TransactionError(Exception):
    """Can't add transaction"""


def add_transaction(
    *,
    user: User,
    from_user: User,
    value: int,
    session: Optional[Session] = None
):
    """Adds a new transaction to the specified user.

    params:
        user: The user to add transaction to.
        from_user: The user where amount is coming from or superuser
        value: The value being added
    """
    if not from_user.superuser and from_user.balance < value:
        raise TransactionError("Insufficient balance")

    session = session or Session(engine)

    transaction = Transaction(user=user, from_user=from_user, value=value)  # pyright: ignore
    session.add(transaction)
    session.commit()
    session.refresh(user)
    session.refresh(from_user)

    for holder in (user, from_user):
        total_income = sum([t.value for t in holder.incomes])  # pyright: ignore
        total_expense = sum([t.value for t in holder.expenses])  # pyright: ignore
        balance = session.get(
            Balance, holder.id
        ) or Balance(user=holder, value=0)  # pyright: ignore
        balance.value = total_income - total_expense
        session.add(balance)

    session.commit()
```

### Garantindo a existencia do usuário `admin` via data-migration.

Começamos criando uma `migration` vazia para efetuarmos a operação
de adição do usuário.

```console
$ docker-compose exec api alembic revision -m "ensure_admin_user"
  Generating /home/app/api/migrations/versions/9aa820fb7f01_ensure_admin_user.py ...  done
```

Repare que dessa vez não usamos `--autogenerate` pois essa migration estará vazia, e neste
caso vamos manualmente escrever o código que desejamos que seja executado.

**Edite** o arquivo criado em `migrations/versions/9aa820fb7f01_ensure_admin_user.py`
 
```python
"""ensure_admin_user

Revision ID: 9aa820fb7f01
Revises: 6f4df3b5e155
Create Date: 2023-01-06 13:13:37.907183

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from dundie.db import engine
from dundie.models.user import User
from sqlmodel import Session

# revision identifiers, used by Alembic.
revision = '9aa820fb7f01'
down_revision = '6f4df3b5e155'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with Session(engine) as session:
        # if admin user already exists it will raise IntegityError
        admin = User(
            name="Admin",
            username="admin",
            email="admin@dm.com",
            dept="management",
            currency="USD",
            password="admin",  # pyright: ignore
        )
        try:
            session.add(admin)
            session.commit()
        except sa.exc.IntegrityError:
            session.rollback()


def downgrade() -> None:
    pass
```

> **IMPORTANTE** a migration acima irá setar o password como `admin` e é muito importante que você defina um password mais complexo ou que faça a alteração corretamente em ambientes de produção.


Salve o arquivo e aplique a migration.

```console
$ docker-compose exec api alembic upgrade head                   
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 6f4df3b5e155 -> 9aa820fb7f01, ensure_admin_user 
``` 

### Atualizando o saldo via CLI 

Agora vamos criar um comando para adicionar saldo via CLI, sempre que feito via CLI 
o usuário será o `admin`


**edite** `dundie/cli.py` e adicione um novo comando no final do arquivo.


```python
# Imports

from dundie.tasks.transaction import add_transaction
from dundie.models.transaction import Transaction, Balance

# No comando `shell`
def shell():
    ...
    _vars = {
      ...
      "Transaction": Transaction,
      "Balance": Balance,
      "add_transaction": add_transaction,
    }

# Comando

@main.command()
def transaction(
    username: str,
    value: int,
):
    """Adds specified value to the user"""

    table = Table(title="Transaction")
    fields = ["user", "before", "after"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        from_user = session.exec(select(User).where(User.username == "admin")).first()
        if not from_user:
            typer.echo("admin user not found")
            exit(1)
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            typer.echo(f"user {username} not found")
            exit(1)

        from_user_before = from_user.balance
        user_before = user.balance
        add_transaction(user=user, from_user=from_user, session=session, value=value)
        table.add_row(from_user.username, str(from_user_before), str(from_user.balance))
        table.add_row(user.username, str(user_before), str(user.balance))

        Console().print(table)
```

E para usar podemos fazer:

```console
$ docker-compose exec api dundie transaction jim-halpert 900
          Transaction           
┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ user        ┃ before ┃ after ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ admin       │ 0      │ -900  │
│ jim-halpert │ 0      │ 900   │
└─────────────┴────────┴───────┘
```

O usuário admin será ficará com saldo negativo e não tem limite de transferencia, 
assim como qualquer usuário que seja super-user.

## Transaction API 

Agora podemos finalmente criar o endpoint na API que vai fornecer a mesma funcionalidade,
porém com algumas diferenças, no caso da API o `from_user` será o usuário que estiver autenticado.


**Edite** `dundie/routes/transaction.py` e adicione o seguinte código:

```python
from fastapi import APIRouter, Body, HTTPException
from dundie.auth import AuthenticatedUser
from dundie.db import ActiveSession
from dundie.models import User
from dundie.tasks.transaction import add_transaction, TransactionError
from sqlmodel import select, Session

router = APIRouter()


@router.post('/{username}/', status_code=201)
async def create_transaction(
    *,
    username: str,
    value: int = Body(embed=True),
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession
):
    """Adds a new transaction to the specified user."""
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        add_transaction(user=user, from_user=current_user, value=value, session=session)
    except TransactionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # At this point there was no error, so we can return
    return {"message": "Transaction added"}
```


Agora podemos adicionar essas rotas no router principal editando `dundie/routes/__init__.py`

```python
from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .transaction import router as transaction_router

main_router = APIRouter()

main_router.include_router(auth_router, tags=["auth"])
main_router.include_router(user_router, prefix="/user", tags=["user"])
main_router.include_router(transaction_router, prefix="/transaction", tags=["transaction"])
```

Neste momento o endpoint já deve aparecer na API.

![](images/transaction_docs.png)


E podemos testar fazendo uma requisição HTTP.

> **Lembre-se** de trocar o token pelo token gerado a partir da URL /token/, por exemplo, gerando um token para o usuário `admin` ou outro superuser permitirá a adição de pontos infinitos.

```console
$ curl -X 'POST' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsLXNjb3R0IiwiZnJlc2giOnRydWUsImV4cCI6MTY3MzQwNjI4MCwic2NvcGUiOiJhY2Nlc3NfdG9rZW4ifQ.qO9ZSwZkDlxsOrkwpbw3zuqCzZ94lm3XPkBVWFzGnBE' \
  --data-raw '{"value": 300}' \
  -k 'http://localhost:8000/transaction/bruno-rocha/'
```

## Consultando transactions 

Agora que já podemos trocar pontos entre usuários vamos criar endpoints onde será possivel consultar
as transações e saldos.

- `POST /transaction/{username}` (feito) - adiciona transação 
- `GET /transaction/` - Lista todas as transações 
    - Se `superuser` exibe todas, caso contrário apenas as próprias.
    - permite filtros: `?from_user=username`, `?to_user=username`
    - permite ordenação: `?order_by=from_user,user,value`
    - permite paginação: `?page=1&size=10` 


Antes de criarmos o endpoint precisamos criar um model de saida, `TransactionResponse`
para evitar o retorno do próprio model do banco de dados.

Se fizermos isso em `dundie/models/transaction.py` teremos um problema de circular imports.

```python
# !!!! Exemplo em dundie/models/transaction.py
from dundie.models.user import User   # <- CIRCULAR IMPORT 


class TransactionResponse(BaseModel):
  user: User
```

Para contornar este problema vamos agora criar um novo arquivo 


> Primeiramente vamos colocar o serializar para Transaction e futuramente
movemos todos os serializers definidos em `models/user.py` para este mesmo módulo.

Neste serializer vamos utilizar `root_validator` para criar campos que são calculados no 
momento da serialização.

*CRIE* `dundie/models/serializers.py`
```python
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
```

Podemos testar no shell com:

```console
$ docker-compose exec api dundie shell
Auto imports: ['settings', 'engine', 'select', 'session', 'User', 
               'Transaction', 'Balance', 'add_transaction']

In [1]: from dundie.models.serializers import TransactionResponse

In [2]: t = session.get(Transaction, 1)

In [3]: TransactionResponse.parse_obj(t)
Out[3]: TransactionResponse(
    value=100, 
    date=datetime.datetime(2023, 1, 6, 12, 21, 55, 30204), 
    user='bruno-rocha', 
    from_user='michael-scott', 
    user_id=2, 
    from_id=1, 
    id=1
)
```

Agora vamos **editar** o arquivo `dundie/routes/transaction.py`

```python
# import 

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from dundie.models import Transaction
from dundie.models.serializers import TransactionResponse

# No final do arquivo

@router.get("/", response_model=Page[TransactionResponse])
async def list_transactions(
    *,
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
    params: Params = Depends(),
    from_user: Optional[str] = None,
    user: Optional[str] = None,
    order_by: Optional[str] = None,
):
    query = select(Transaction)

    # Optional `AND` filters
    if user:
        query = query.join(User, Transaction.user_id == User.id).where(User.username == user)
    if from_user:
        FromUser = aliased(User)  # aliased needed to desambiguous the join
        query = query.join(FromUser, Transaction.from_id == FromUser.id).where(
            FromUser.username == from_user
        )

    # Mandatory access filter
    # regular users can only see their own transactions
    if not current_user.superuser:
        query = query.where(
            (Transaction.user_id == current_user.id) | (Transaction.from_id == current_user.id)
        )

    # Ordering based on &order_by=date (asc) or -date (desc)
    if order_by:
        order_text = text(order_by.replace("-", "") + " " + ("desc" if "-" in order_by else "asc"))
        query = query.order_by(order_text)

    # wrap response_model in a pagination object {"items": [], total, page, size }
    return paginate(query=query, session=session, params=params)
```

Agora temos um novo endpoint listando todas as transactions e com os filtros que especificamos.

![](images/transaction_list.png)

```console
$ curl 'GET' -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJicnVuby1yb2NoYSIsImZyZXNoIjp0cnVlLCJleHAiOjE2NzM0ODg0NzksInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0.TLDOYKsA5TRU049_xjlir4wklhyTi0D-tkdES4KDako' \
    -k 'http://localhost:8000/transaction/\
    ?page=1&size=2&from_user=michael-scott&user=bruno-rocha&order_by=-date'
```
```json
#+RESPONSE
{
  "items": [
    {
      "id": 12,
      "value": 300,
      "date": "2023-01-10T17:08:29.953452",
      "user": "bruno-rocha",
      "from_user": "michael-scott",
      "from_id": 1,
      "user_id": 2
    },
    {
      "id": 11,
      "value": 112,
      "date": "2023-01-10T17:07:49.296277",
      "user": "bruno-rocha",
      "from_user": "michael-scott",
      "from_id": 1,
      "user_id": 2
    }
  ],
  "total": 6,
  "page": 1,
  "size": 2
}
#+END
```

## Revisão da API 

Agora que já temos bastante funcionalidade na API vamos revisar e identificar o que está faltando.

### Auth 

- POST /token - login via formulário para gerar acccess token 
- POST /refresh_token - Obter um novo token sem a necessidade de fazer login novamente

### User 

- GET /user/ -  Lista todos os usuários
- GET /user/{username} - Lista um usuário específico
- POST🔒 /user/ - Cria um novo usuário 
- PATCH🔒 /user/{username} - Altera informações do usuário 
- POST  /user/{username}/password - Altera a senha do usuário (?pwd_reset_token ou 🔒)
- POST /user/pwd_reset_token/ - Solicita um token via email para resetar a senha (?email)

### Transaction 

- POST🔒 /transaction/ - Cria uma nova transaction de `from_user para user`
- GET🔒 /transaction/ - Lista transactions do usuário logado (ou todas em caso de superuser)
    - filters: `user`, `from_user`
    - sort: `order_by=date` (asc) ou `-date` (desc)
    - pagination: `page`, `size`


## Exibir saldo total em `/user/`

Na listagem de usuário está faltando exibir o saldo total do usuário, 
esta é uma informação sensivel e portanto estará disponível apenas em
alguns casos.

- `?add_balance=true` for passado na URL das rotas GET de /user/
- O usuário logado é superuser ou
- O usuário logado está acessando sua própria conta


**EDITE** o arquivo `dundie/auth.py` e vamos adicionar mais uma dependencia 
baseada em autenticação.

```python

async def show_balance_field(
    *,
    request: Request,
    show_balance: Optional[bool] = False,  # from /user/?show_balance=true
) -> bool:
    """Returns True if one of the conditions is met.
    1. show_balance is True AND
    2. authenticated_user.superuser OR
    3. authenticated_user.username == username
    """
    if not show_balance:
        return False

    username = request.path_params.get("username")

    try:
        authenticated_user = get_current_user(token="", request=request)
    except HTTPException:
        authenticated_user = None

    if any(
        [
            authenticated_user and authenticated_user.superuser,
            authenticated_user and authenticated_user.username == username,
        ]
    ):
        return True

    return False


ShowBalanceField = Depends(show_balance_field)
```

Agora precisamos de um serializer contendo o campo `balance`

**EDITE** `dundie/models/user.py`


```python
# Logo abaixo da classe UserResponse

class UserResponseWithBalance(UserResponse):
    balance: Optional[int] = None

    @root_validator(pre=True)
    def set_balance(cls, values: dict):
        """Sets the balance of the user"""
        instance = values["_sa_instance_state"].object
        values["balance"] = instance.balance
        return values
```


Agora **EDITE** o `dundie/routes/user.py` e vamos usar a dependencia
nos endpoints `list_users` e `get_user_by_username`

```python
# IMPORTS 
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from dundie.auth import ShowBalanceField
from dundie.models.user import UserResponseWithBalance

# list_users 

@router.get(
    "/",
    response_model=List[UserResponse] | List[UserResponseWithBalance],
    response_model_exclude_unset=True,
)
async def list_users(
    *, session: Session = ActiveSession, show_balance_field: bool = ShowBalanceField
):
    """List all users.

    NOTES:
    - This endpoint can be accessed with a token authentication
    - show_balance query parameter takes effect only for authenticated superuser.
    """
    users = session.exec(select(User)).all()
    if show_balance_field:
        users_with_balance = parse_obj_as(List[UserResponseWithBalance], users)
        return JSONResponse(jsonable_encoder(users_with_balance))
    return users

# get user by username 
@router.get(
    "/{username}/",
    response_model=UserResponse | UserResponseWithBalance,
    response_model_exclude_unset=True,
)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str, show_balance_field: bool = ShowBalanceField
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if show_balance_field:
        user_with_balance = parse_obj_as(UserResponseWithBalance, user)
        return JSONResponse(jsonable_encoder(user_with_balance))
    return user
```

## A API está pronta!

![](images/api_final.png)

Bom.. nada está pronto enquanto não tiver cobertura de testes.

## Testando

O Pipeline de testes será

0. Garantir que o ambiente está em execução com o docker-compose
1. Garantir que existe um banco de dados `dundie_test` e que este banco está
   vazio.
2. Executar as migrations com alembic e garantir que funcionou
3. Executar os testes com Pytest
4. Apagar o banco de dados de testes

Vamos adicionar um comando `reset_db` no cli

> **NOTA** muito cuidado com esse comando!!!

edite `dundie/cli.py`
```python
# imports
from .db import engine, SQLModel


# Final
@main.command()
def reset_db(
    force: bool = typer.Option(
        False, "--force", "-f", help="Run with no confirmation"
    )
):
    """Resets the database tables"""
    force = force or typer.confirm("Are you sure?")
    if force:
        SQLModel.metadata.drop_all(engine)
```

Em um ambiente de CI geralmente usamos `Github Actions` ou `Jenkins` para executar
esses passos, em nosso caso vamos usar um script em bash para executar essas tarefas.

> **NOTA** esses mesmos passos podem ser traduzidos para um job no Github actions, inclusive 
> reaproveitando o mesmo script.

`test.sh`
```bash
#!/usr/bin/bash

# Start environment with docker-compose
DUNDIE_DB=dundie_test docker-compose up -d

# wait 5 seconds
sleep 5

# Ensure database is clean
docker-compose exec api dundie reset-db -f
docker-compose exec api alembic stamp base

# run migrations interactively so ensure unlocked transactions.
docker-compose exec api alembic upgrade base
docker-compose exec api alembic upgrade +1

# Data migrations cannot run on locked so run separately
docker-compose exec api alembic upgrade head

# run tests
docker-compose exec api pytest -v -l --tb=short --maxfail=1 tests/

# Stop environment
docker-compose down
```

Para os tests vamos utilizar o Pytest para testar algumas rotas da API,
com o seguinte fluxo

# Setup 

01. Obter um token para o usuário admin
00. Criar usuário1
00. Obter um token para o usuário1
00. Criar usuario2
00. Obter um token para o usuario2

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

E agora adicionamos alguns testes em `tests/test_api.py`

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

```console
$ chmod +x test.sh
```
e
```console
$ ./test.sh
[+] Running 3/3
 ⠿ Network fastapi-workshop_default  Created                      0.0s
 ⠿ Container fastapi-workshop-db-1   Started                      0.5s
 ⠿ Container fastapi-workshop-api-1  Started                      1.4s

INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running stamp_revision f432efb19d1a ->
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ee59b23815d3, initial
INFO  [alembic.runtime.migration] Running upgrade 4634e842ac70 -> f9b269f8d5f8, post

========================= test session starts =========================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /home/app/api
plugins: order-1.0.1, anyio-3.6.2
collected 6 items

tests/test_api.py::test_post_create_user1 PASSED                [ 16%]
tests/test_api.py::test_reply_on_post_1 PASSED                  [ 33%]
tests/test_api.py::test_post_list_without_replies PASSED        [ 50%]
tests/test_api.py::test_post1_detail PASSED                     [ 66%]
tests/test_api.py::test_all_posts_from_user1 PASSED             [ 83%]
tests/test_api.py::test_all_posts_from_user1_with_replies PASSED [100%]

========================== 6 passed in 1.58s ==========================

[+] Running 3/3
 ⠿ Container fastapi-workshop-api-1  Removed                      0.8s
 ⠿ Container fastapi-workshop-db-1   Removed                      0.6s
 ⠿ Network fastapi-workshop_default  Removed                      0.5s
```


## Desafios finais

Lembra-se do nosso database?

![](database.png)

Em nosso projeto está faltando adicionar os models para `Social` e `Like`

### Social

O objetivo é que um usuário possa seguir outro usuário,
para isso o usuário precisará estar autenticado e fazer um `post` request em
`POST /user/follow/{id}` e sua tarefa é implementar esse endpoint armazenando
o resultado na tabela `Social`.

- Passo 1
  Edite `dundie/models/user.py` e adicione a tabela `Social` com toda a
  especificação e relacionamentos necessários. (adicione esse model ao `__init__.py`
- Passo 2
  Execute dentro do shell do container `alembic revision --autogenerate -m 'social'`
  para criar a migração
- Passo 3
  Aplique as migrations de tabela com `alembic upgrade head`
- Passo 4
  Crie o Endpoint em `dundie/routes/user.py` com a lógica necessária e adicione ao
  router `__init__.py`
- Passo 5
  Escreva um teste em `tests_user.py` para testar a funcionalidade de um usuário
  seguir outro usuário
- Passo 6
  Em `dundie/routes/user.py` cria uma rota `/timeline` que ao acessar `/user/timeline`
  irá listar todos os posts de todos os usuários que o user autenticado segue.

### Like

O objetivo é que um usuário possa enviar um like em um post e para isso
precisará estar autenticado e fazer um `post` em `/post/{post_id}/like/`
e a sua tarefa é implementar esse endpoint salvando o resultado na tabela `Like`.

- Passo1
  Edite `dundie/model/post.py` e adicione a tabela `Like` com toda a especificação
  necessária com relacionamentos e adicione ao model `__init__.py`
- Passo 2
  Execute dentro do shell do container `alembic revision --autogenerate -m 'like'`
  para criar a migração
- Passo 3
  Aplique as migrations de tabela com `alembic upgrade head`
- Passo 4
  Crie o endpoint em `dundie/routes/post.py` com a lógica necessária e adicione ao
  routes `__init__.py`
- Passo 5
  Escreva um teste onde um user pode deixar um like em um post
- Passo 6
  Em `dundie/routes/post.py` crie uma rota `/likes/{username}/` que retorne
  todos os posts que um user curtiu.

### Desafio extra opcional

Use React ou VueJS para criar um front-end para esta aplicação :)
