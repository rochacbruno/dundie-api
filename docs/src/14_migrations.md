# Migrations

Portanto agora já temos uma tabela mapeada e um conexão com o banco de dados
precisamos agora garantir que a estrutura da tabela existe dentro do banco
de dados.

Para isso vamos usar a biblioteca `alembic` que gerencia migrações, ou seja,
alterações na estrutura das tabelas e automação de alteração em dados.

Começamos na raiz do repositório, no seu terminal rodando:

```bash
alembic init migrations
```

O alembic irá criar um arquivo chamado `alembic.ini` e uma pasta chamada `migrations` que servirá para armazenar o histórico de alterações do banco de dados.

Começaremos **editando** o arquivo `migrations/env.py`

> Atenção nos comentários do snippet abaixo explicando exatamente onde efetuar cada uma das edições

```python
# 1 - No topo do arquivo adicionamos
from dundie import models
from dundie.db import engine
from dundie.config import settings


# 2 - Perto da linha 23 mudamos de
# target_metadata = None
# para:
target_metadata = models.SQLModel.metadata

# 3 - Na função `run_migrations_offline()` mudamos
# url = config.get_main_option("sqlalchemy.url")
# para:
url = settings.db.uri

# 4 - Na função `run_migration_online` mudamos
# connectable = engine_from_config...
# para:
connectable = engine
```

Agora precisamos fazer só mais um ajuste
**edite** `migrations/script.py.mako` e em torno da linha 10
adicione

```python
#from alembic import op
#import sqlalchemy as sa
import sqlmodel  # linha NOVA
```

Agora sim podemos começar a usar o **alembic** para gerenciar as
migrations, precisamos executar este comando dentro do shell do container.


## Executando comandos dentro do container 

```admonish important "IMPORTANTE"
Todos os comandos a partir de agora serão executados no shell dentro do container e para fazer isso usaremos sempre `docker-compose exec` antes que qualquer comando.
```

Experimente: `docker-compose exec api /bin/bash`

```console
$ docker-compose exec api /bin/bash
app@c5dd026e8f92:~/api$ # este é o shell dentro do container api

# digite exit para sair
```

Podemos redirecionar comandos diretamente para dentro do container com `docker-compose exec api [comando a ser executado]` 


## Gerando e aplicando migrations 

Agora para gerar um registro inicial de migration usaremos o comando `alembic revision --autogenerate` e isso será executado dentro do container conforme exemplo abaixo:

```console
$ docker-compose exec api alembic revision --autogenerate -m "initial"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
  Generating /home/app/api/migrations/versions/ee59b23815d3_initial.py ...  done
```

Repare que o alembic identificou o nosso model `User` e gerou uma migration
inicial que fará a criação desta tabela no banco de dados.

Podemos aplicar a migration rodando dentro do container com `alembic upgrade head`:

```console
$ docker-compose exec api alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ee59b23815d3, initial
```

E neste momento a tabela será criada no Postgres e já podemos começar a interagir via SQL client ou através da classe `User` que modelamos anteriormente.

```admonish tip "DICA"  
Pode usar um client como [https://antares-sql.app](https://antares-sql.app) para se conectar ao banco de dados, usar o **psql** na linha de comando ou abrir o shell do ipython dentro do container.
```

## Acessando o banco de dados através do shell

```console
$ docker-compose exec api ipython
# Agora está no ipython dentro do shell do container
In [1]: 
```

Digite

```python
from sqlmodel import Session, select
from dundie.db import engine
from dundie.models import User

with Session(engine) as session:
    print(list(session.exec(select(User))))
```

O resultado será uma lista vazia `[]` indicando que ainda não temos nenhum usuário no banco de dados.

> Digite `exit` para sair do ipython.

```admonish note "Conclusão"
Foi preciso muito **boilerplate** para conseguir interagir com banco de dados através do shell portanto para facilitar a nossa vida vamos adicionar uma aplicação `cli` onde vamos poder executar tarefas administrativas via linha de comando como criar ou listar usuários. -->
```
