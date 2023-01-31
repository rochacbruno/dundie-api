# Transaction CLI

Agora vamos criar um comando para adicionar saldo via CLI, sempre que feito via CLI  o usuário
de origem dos pontos `from_id` será o `admin`.

O comando vai simplesmente chamar a função `add_transaction` que criamos anteriormente mas colocaremos
lógica adicional para garantir a existencia dos usuários e para formatar os dados aprensentados em
uma tabela no terminal.


**EDITE** `dundie/cli.py` e adicione um novo comando no final do arquivo.


```python
# No topo

from dundie.tasks.transaction import add_transaction
from dundie.models.transaction import Transaction, Balance

# No comando `shell` adicione novos objetos
def shell():
    ...
    _vars = {
      ...
      "Transaction": Transaction,
      "Balance": Balance,
      "add_transaction": add_transaction,
    }

# Crie o comando que adiciona transactions 
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

E para usar podemos fazer o seguinte  no terminal:

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

```admonish todo "Tarefa"
Ao chamarmos o comando `dundie transaction` assim como o `user-list` o retorno é mostrado
em uma tabela formatada no terminal, em alguns casos seria interessante poder passar um
argumento `--format=json` e obter o retorno em formato JSON para posterior tratamento.

Consegue adicionar essa funcionalidade?
```

Agora vamos partir para a API adicionando a mesma funcionalidade -->
