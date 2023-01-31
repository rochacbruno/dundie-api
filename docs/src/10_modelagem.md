# Modelagem

## Definindo os models com Pydantic

Esta será a modelagem do banco de dados completo, mas começaremos apenas com a tabela de usuários.

![database](images/database.png)

[https://dbdesigner.page.link/GqDU95ApwZs7a9RH9](https://dbdesigner.page.link/GqDU95ApwZs7a9RH9)

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
        """"Users belonging to management dept are admins."""
        return self.dept == "management"
```

Para que seja possivel importar e o **SQLAlchemy** reconhecer o nosso objeto **EDITE** arquivo `dundie/models/__init__.py` adicione

```python
from sqlmodel import SQLModel
from .user import User

__all__ = ["User", "SQLModel"]
```

> **NOTA** as tabelas Balance e Transaction iremos definir posteriormente.

Agora podemos nos conectar com o banco de dados ->
