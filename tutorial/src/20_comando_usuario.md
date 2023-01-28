# Comando para criar usuários

**EDITE** `dundie/cli.py` e adicione no topo do arquivo:

```python 
from dundie.models.user import generate_username
```


e no final adicione um novo comando:


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

A função `create_user` será exposta na CLI como o subcomando  `create-user`, ou seja, `_` será substituido por `-` então no terminal execute para ver a mensagem de ajuda `dundie create-user --help`:

```console
$ docker-compose exec api dundie create-user --help
                                                    
 Usage: dundie create-user [OPTIONS] NAME EMAIL PASSWORD DEPT            
                                                    
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

E então execute o comando para criar o usuário para o gerente **Michael Scott**

```admonish tip
No terminal quando uma linha fica muito longa podemos adicionar 
uma quebra de linha com `\` e o terminal vai entender que é uma
única linha.

E no caso de argumentos com espaço como o nome "Michael Scott" precisamos 
usar aspas para o terminal entender que é um único argumento.
```

Crie o usuário:

```console
$ docker-compose exec api dundie create-user \
"Michael Scott" mscott@dm.com boss123 management 

created michael-scott user
```

E para listar o usuário criado:

```console
$ docker-compose exec api dundie user-list

                              dundie users                               
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ name          ┃ username      ┃ dept       ┃ email         ┃ currency ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Michael Scott │ michael-scott │ management │ mscott@dm.com │ USD      │
└───────────────┴───────────────┴────────────┴───────────────┴──────────┘
```

Agora podemos finalmente começar a criar a nossa API -->
