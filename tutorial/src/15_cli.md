# Criando a CLI

Command Line Interface é uma parte importante de todo serviço, é através dessa ferramanta que geralmente
os administradores do serviço interagem com ele, seja para realizar tarefas de manutenção, configuração
ou recuperar o sistema em caso de falhas.

Vamos criar uma CLI para o nosso serviço, para isso vamos usar o [typer](https://typer.tiangolo.com/),
que é uma das melhores bibliotecas para criar CLIs em Python.

Começaremos adicionando um comando `shell` que abrirá um shell interativo com os objetos da aplicação e um outro
comando `user-list` para listar todos os usuários cadastrados.

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
```admonish tip
Não se esqueça de salvar os arquivo modificado :)
```

E agora podemos executar.

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

O comando `user-list` para listar todos os usuários (que por enquanto irá retornar uma tabela vazia)

```console
$ docker-compose exec api dundie user-list
                dundie users
┏━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ name ┃ username ┃ dept ┃ email ┃ currency ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
└──────┴──────────┴──────┴───────┴──────────┘
```

e o comando `shell` que irá abrir um shell interativo com os objetos da aplicação.

```console
$ docker-compose exec api dundie shell
Auto imports: ['settings', 'engine', 'select', 'session', 'User']

In [1]: session.exec(select(User))
Out[1]: <sqlalchemy.engine.result.ScalarResult at 0x7fb539d5e170>

In [2]: settings.db
Out[2]: <Box: {'connect_args': {}, 'uri': 'postgresql://postgres:postgres@db:5432/dundie', 'echo': False}>
```

Ainda não temos usuários cadastrados pois ainda está faltando uma parte importante
que é o **hash de senhas** para os usuários, vamos resolver -->
