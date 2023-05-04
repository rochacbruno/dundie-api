# Definindo um pipeline

O Pipeline de testes será

0. Garantir que o ambiente está em execução com o docker compose
1. Garantir que existe um banco de dados `dundie_test` e que este banco está
   vazio.
2. Executar as migrations com alembic e garantir que funcionou
3. Executar os testes com Pytest
4. Apagar o banco de dados de testes

Vamos adicionar um comando `reset_db` no cli

```admonish caution "CUIDADO"
Muito cuidado com esse comando, ele apaga todo o conteúdo do banco de dados!!!
```

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

O comando acima poderá ser executado com a flag `-f` que irá pualr a etapa de confirmação.

Em um ambiente de CI geralmente usamos `Github Actions` ou `Jenkins` para executar
esses passos, em nosso caso vamos usar um script em bash para executar essas tarefas,
no treinamento **Python Automation** que também faz parte do pacote Python Expert será
abordado como automatizar esses processos usando os principais serviços de CI.


Confira o conteúdo do arquivo `test.sh` na raiz do repositório.

```bash
#!/usr/bin/bash

# Start environment with docker compose
DUNDIE_DB=dundie_test docker compose up -d

# wait 5 seconds
sleep 5

# Ensure database is clean
docker compose exec api dundie reset-db -f
docker compose exec api alembic stamp base

# run migrations
docker compose exec api alembic upgrade head

# run tests
docker compose exec api pytest -v -l --tb=short --maxfail=1 tests/

# Stop environment
docker compose down
```

1. definimos um banco de dados diferente usando a variável `DUNDIE_DB` 
2. iniciamos o ambiente com o docker compose
3. esperamos 5 segundos para garantir que o banco de dados está pronto 
4. resetamos o banco de dados 
5. executamos as migrations para garantir que temos todas as tabelas e dados 
6. executamos os testes usando pytest
7. finalizamos o ambiente

```admonish note "NOTA"
Em caso de falha nos testes o ambiente não será parado, permitindo assim o debugging com o ambiente em execução.
```

O próximo passo é configurar o nosso test-runner, o pytest -->
