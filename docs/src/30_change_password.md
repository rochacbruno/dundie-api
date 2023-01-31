# Change Password

O endpoint de alteração de senha precisa ficar separado do perfil pois este endpoint precisa de alguns detalhes extras:

01. O usuário precisa preencher a senha e a confirmação
00. A mudança pode ser feita pelo próprio usuário, pelo superuser ou através de um token requisitado por email (funcionalidade de **esqueci a senha**)

Começamos adicionando o serializer para receber o request da alteração do password.

**EDITE** `models/user.py`
```python

# No topo
from fastapi import HTTPException, status
from dundie.security import get_password_hash

...

# No final
class UserPasswordPatchRequest(BaseModel):
    password: str
    password_confirm: str

    @root_validator(pre=True)
    def check_passwords_match(cls, values):
        """Checks if passwords match"""
        if values.get("password") != values.get("password_confirm"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        return values

    @property
    def hashed_password(self) -> str:
        """Returns hashed password"""
        return get_password_hash(self.password)
```

Para editar o password do usuário teremos as seguintes condições

```python
# O usuário pode editar o próprio password
current_user == user

# O usuário pode editar o password de outro usuário se for superuser
current_user.supersuser is True

# ou se o usuário tiver um token válido
Query("?pwd_reset_token") is valid
```

Vamos implementar a lógica acima como uma dependencia do FastAPI, usaremos esta dependencia na rota 
de alteração de senha e a dependência irá garantir que pelo menos um dos requisitos seja satisfeito.

**EDITE** `dundie/auth.py` e no final:
```python
async def get_user_if_change_password_is_allowed(
    *,
    request: Request,
    pwd_reset_token: Optional[str] = None,  # from path?pwd_reset_token=xxxx
    username: str,  # from /path/{username}
) -> User:
    """Returns User if one of the conditions is met.
    1. There is a pwd_reset_token passed as query parameter and it is valid OR
    2. authenticated_user is supersuser OR
    3. authenticated_user is User
    """
    target_user = get_user(username)  # The user we want to change the password
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        valid_pwd_reset_token = get_current_user(token=pwd_reset_token or "") == target_user
    except HTTPException:
        valid_pwd_reset_token = False

    try:
        authenticated_user = get_current_user(token="", request=request)
    except HTTPException:
        authenticated_user = None

    if any(
        [
            valid_pwd_reset_token,
            authenticated_user and authenticated_user.superuser,
            authenticated_user and authenticated_user.id == target_user.id,
        ]
    ):
        return target_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to change this user's password",
    )


CanChangeUserPassword = Depends(get_user_if_change_password_is_allowed)
```

Agora temos `CanChangeUserPassword` como dependencia para usar em uma rota do FastAPI
isso vai garantir que a URL só será executada se todas as condições da dependencia foram
resolvidas.

E agora em `routes/user.py` vamos criar uma rota com o método `POST`

```admonish note "NOTA"
O ideal para seguir a semantica REST seria criar este método como **PATCH** porém formulários HTML permitem apenas GET e POST e para facilitar o trabalho do front-end vamos usar POST.
```

```python
@router.post("/{username}/password/", response_model=UserResponse)
async def change_password(
    *,
    session: Session = ActiveSession,
    patch_data: UserPasswordPatchRequest,
    user: User = CanChangeUserPassword
):
    user.password = patch_data.hashed_password  # pyright: ignore
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

Agora podemos testar a rota de alteração de senha, autenticando com o token válido para o usuário michael-scott por exemplo:

```bash
curl -X 'POST' \
 -H 'Authorization: Bearer ...' \
 -H 'Content-Type: application/json' 
 --data-raw '{"password": "boss1234", "password_confirm": "boss1234"}' \
 -k 'http://localhost:8000/user/michael-scott/password/'
```

O usuário `michael-scott` sendo um superuser, também tem permissão para alterar senha de outros usuários,

Agora imagine que um usuário esqueceu a própria senha, mas ao invés de pedir para o gerente ele quer ele
mesmo alterar a senha, para isso vamos criar um endpoint para enviar um email com um token válido para
alterar a senha e acessar o mesmo endpoint. --> 
