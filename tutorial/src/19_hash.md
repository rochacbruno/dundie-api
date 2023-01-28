# Criando um hash

Para fazer com que o password dos usuários seja salvo como um hash ao invés de plain-text
vamos criar uma função para criar o hash e outra para verificar.

Além disso vamos criar uma classe herdando de `str` e customizar o método `validate`
desta forma podemos usar esta classe na definição de campo do nosso model `User` e 
o pydantic vai chamar o método `validate` para transformar o valor do campo em um hash.

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

E no final de `dundie/models/user.py` uma função para gerar os usernames, transformando nomes completos como **Bruno Rocha** em um **slug** como **bruno-rocha**

```python 
def generate_username(name: str) -> str:
    """Generates a slug username from a name"""
    return name.lower().replace(" ", "-")
```

Agora sim está tudo pronto para adicionarmos ao nosso CLI um comando para criar novos usuários --> 
