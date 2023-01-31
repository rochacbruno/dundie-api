# Data Migrations

Até agora usamos o **alembic** para criar migrations de estrutura (DDL) em operações de criação ou alteração
de campos e tabelas.

Entretanto, em alguns casos precisamos criar dados para alimentar a aplicação, como por exemplo
criar um usuário administrador para que possamos acessar a aplicação.

Sempre que precisar garantir a existência de dados alimentados em tabelas do sistema usaremos 
o conceito de **Data Migrations**.

Começamos criando uma `migration` vazia para efetuarmos a operação de adição do usuário.

```console
$ docker-compose exec api alembic revision -m "ensure_admin_user"
  Generating /home/app/api/migrations/versions/9aa820fb7f01_ensure_admin_user.py ...  done
```

Repare que dessa vez não usamos `--autogenerate` pois essa migration estará vazia, e neste
caso vamos manualmente escrever o código que desejamos que seja executado.

**Edite** o arquivo criado em `migrations/versions/9aa820fb7f01_ensure_admin_user.py`

> **OBS** O arquivo criado ai no seu sistema pode ter um nome diferente, mas o conteúdo é o mesmo.

```python
"""ensure_admin_user

Revision ID: 9aa820fb7f01
Revises: 6f4df3b5e155
Create Date: 2023-01-06 13:13:37.907183

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from dundie.models.user import User  # NEW
from sqlmodel import Session  # NEW

# revision identifiers, used by Alembic.
revision = '9aa820fb7f01'
down_revision = '6f4df3b5e155'
branch_labels = None
depends_on = None


def upgrade() -> None:  # NEW
    bind = op.get_bind()
    session = Session(bind=bind)

    admin = User(
        name="Admin",
        username="admin",
        email="admin@dm.com",
        dept="management",
        currency="USD",
        password="admin",  # pyright: ignore
    )
    # if admin user already exists it will raise IntegrityError
    try:
        session.add(admin)
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()


def downgrade() -> None:
    pass
```

```admonish todo "Tarefa"
A migration acima irá setar o password como `admin` e é muito importante que você defina um password mais complexo ou que faça a alteração corretamente em ambientes de produção.

Uma dica é que tenha no arquivo de settings um campo para definir o password inicial de admin e então na migration ao invés
de passarmos `admin` podemos ler de `settings.DEFAULT_ADMIN_PASSWORD`, para essa variável existir ela precisa estar no arquivo `default.toml` e então poderá ser sobrescrita usando variável de ambiente `DUNDIE_DEFAULT_ADMIN_PASSWORD`.

Essa alteração eu vou deixar para você fazer, pode ser depois, no final deste tutorial todas as tarefas estarão listadas.
```

Agora salve o arquivo e aplique a migration.

```console
$ docker-compose exec api alembic upgrade head                   
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 6f4df3b5e155 -> 9aa820fb7f01, ensure_admin_user 
```

Agora toda vez que as migrations forem aplicadas, ação que será executada sempre que houver nova atualização ou deploy, 
garantimos que o usuário admin será criado.

E agora que temos a certeza que o `admin` vai sempre existir podemos partir para a criação de um comando na CLI -->
