# Definindo Serializers

Agora vamos criar endpoints na API para efetuar as operações que fizemos
através da CLI, teremos as seguintes rotas:

- `GET /user/` - Lista todos os usuários
- `POST /user/` - Cadastro de novo usuário
- `GET /user/{username}/` - Detalhe de um usuário

### Serializers

A primeira coisa que precisamos é definir serializers, que são models
intermediários usados para serializar e de-serializar dados de entrada e saída
da API e eles são necessários pois não queremos export o model do
banco de dados diretamente na API e também queremos a possibilidade de serializar 
campos opcionais dependendo do nível de acesso do usuário, 
por exemplo, admins poderão ver mais campos que usuários regulares.

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

Podemos testar os serializers em nosso shell só para ter certeza do funcionamento correto.

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

Como pode ver acima podemos criar usuários via API e serializar usando o `UserRequest` e só a partir dele criar a instancia de `User`  que iremos salvar no banco de dados.  

E da mesma forma podemos fazer o caminho inverso, serializando do banco de dados para a API em JSON.

```python
In [19]: bruno = session.exec(select(User).where(User.username=="bruno-rocha")).first()

In [20]: from dundie.models.user import UserResponse

In [21]: UserResponse.parse_obj(bruno).json()
Out[21]: '{"name": "Bruno Rocha", "username": "bruno-rocha", "dept": "Sales", "avatar": null, "bio"
: null, "currency": "USD"}'
```
