# Protegendo rotas

Apenas super usuários terão permissão para criar novos usuários, portanto
vamos proteger a view `POST /user/` com autenticação via **TOKEN**


**EDITE** `dundie/auth.py` e adicione no final uma dependencia para 
garantir que o usuário autenticado é super usuário.

```python
async def get_current_super_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a super user"
        )
    return current_user


SuperUser = Depends(get_current_super_user)
```

Agora vamos usar essa dependencia para garantir o super usuário em nossa rota 
**EDITE** `dundie/routes/user.py`  

No topo próximo a linha 9

```python
from dundie.auth import SuperUser
```

E no roteamento da view `create_user` como parametro para o decorator `.post` passamos uma lista de
dependencias que sejam satisfeitas pelo FAstAPI antes de executar o código da view, ou seja, o código só será executado caso o usuário autenticado via token seja um superusuário.

```python

@router.post("/", response_model=UserResponse, status_code=201, dependencies=[SuperUser])
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    ...

```

Como adicionamos `dependencies=[SuperUser]` no roteamento e isso é o suficiente para o FastAPI detectar que existe pelo menos uma URL que necessita de autenticação e agora já teremos os controles de autenticação na API.

![Auth](images/auth_form.png)


Ao tentar criar um usuário sem autenticar teremos agora um erro `HTTP_401_UNAUTHORIZED` e se o usuário autenticado não for um superuser termos o erro `HTTP_403_FORBIDDEN`

Os requests vão precisar do token, portanto o usuário primeiro precisa pedir um token na URL `/token` e depois usar este token na requisição protegida 

```bash
curl -X 'POST' \
  'http://localhost:8000/user/?fresh=false' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsLXNjb3R0IiwiZnJlc2giOnRydWUsImV4cCI6MTY3MTgyOTc2NCwic2NvcGUiOiJhY2Nlc3NfdG9rZW4ifQ.wdIUyJS9TX2Ku8BMI_AIJhAXQb-TSHmX11qKs5C4PF0' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Kevin Malone",
  "email": "kevin@dm.com",
  "dept": "Sales",
  "password": "stacy"
}'

```

