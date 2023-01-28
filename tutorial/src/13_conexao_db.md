# Conexão com o DB

Para conectar com o banco de dados, precisamos criar um objeto `engine`, este objeto armazena as configurações
como o endereço do banco, usuário e senha. O objeto `engine` é o responsável por executar as consultas SQL que
usaremos para definir as tabelas e também para consultar e alterar dados.

**EDITE** o arquivo `dundie/db.py` e deixe conforme o código abaixo:

`dundie/db.py`
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
dados e para isso usamos as variáveis que lemos do `settings`, o objeto `settings` será capaz de carregar 
essas variáveis do ambiente ou dos arquivos `.toml` que definimos para configuração.

```admonish note
O comentário `# pyright: ignore` só é necessário caso você esteja usando um editor com LSP que faz verificação
de tipos, como o VSCode ou Neovim. Este comentário faz com que o LSP ignore a checagem de tipos para essas linhas,
e é útil pois como esses valores são dinâmicos podemos receber qualquer tipo.
```
