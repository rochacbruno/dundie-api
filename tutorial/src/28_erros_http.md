# Erros HTTP

Quando as coisas dão errado precisamos informar o cliente HTTP com o código de status correto, erros podem acontecer
quando ocorre uma falha inesperada no servidor, quando o recurdo solicitado não existe ou quando o cliente efetua 
uma requisição inválida.

Vamos tentar duplicar a criação de um usuário fazendo novamente a mesma chamada POST e a mensagem que receberemos é:

Faça essa chamada mais de 1x:

```console
curl -X 'POST' -H 'Content-Type: application/json' \
  --data-raw '{"email": "pam@dm.com", "dept": "Accounting", "password": "jimjim", "name": "Pam Besly"}' \
  -k 'http://localhost:8000/user/'
```


```http
HTTP/1.1 500 Internal Server Error

Internal Server Error
```

A mensagem de erro não ajuda muito a sabermos o que ocorreu de fato e portanto podemos curtomizar este comportamento.

Quando temos este caso expecifico o código de erro correto é o `409 Conflict` que innforma que o estado interno está em conflito com o estado que está sendo enviado no request, ou seja, estamos tentando criar um usuário que já existe.

Para customizar este comportamento podemos editar o arquivo `routes/user.py`

```python
# No topo
from sqlalchemy.exc import IntegrityError

# Na função `create_user`
async def create_user(.......):
    ...
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists")
```

A exception `IntegrityError` será levantada para qualquer problemas encontrado no banco de dados portanto não é ainda a melhor opção, precisamos ser mais especificos para ajudar quem está usando a API, portanto vamos fazer as seguintes modificações:

1. Continuar tratando a IntegrityError porém com o código 500 e mensagem de erro genérica.
2. Adicionar um guard para garantir que o usuário a ser criado não existe.


```python
@router.post(
    "/", response_model=UserResponse, status_code=201, dependencies=[SuperUser]
)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Database IntegrityError")

    session.refresh(db_user)
    return db_user
```

E agora sim teremos o retorno esperado

```http
HTTP/1.1 409 Conflict
Username already taken
```

E no caso de um outro erro de integridade ai invés de mostrar apenas o erro 500 genérico informamos especificamente que se trata de um problema no banco de dados, porém sem expor o erro diretamente.

```admonish note "NOTA"
Uma boa prática seria colocar um logger ou um analisador de exceptions como o NewRelic ou o Sentry, faremos isso em outra parte do treinamento.
```

Vamos agora continuar implementando as rotas de usuário -->
