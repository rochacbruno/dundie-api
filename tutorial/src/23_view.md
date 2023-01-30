# Criando as Views

Agora criaremos as views (funções) para expor os serializers com os usuários que acessaremos
usando a sessão de conexão ao banco de dados.

**edite** `dundie/routes/user.py`

```python
from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from dundie.db import ActiveSession
from dundie.models.user import User, UserRequest, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(*, session: Session = ActiveSession):
    """List all users."""
    users = session.exec(select(User)).all()
    return users


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```

Acima criamos 3 views, uma para listar todos os usuários, uma para listar apenas um usuário e outra para criar um novo usuário.

repare que a rota de criação de um novo usuário temos 2 detalhes diferentes: 1) estamos usando o método `post` e 2) estamos retornando o status code `201` (criado) em caso de sucesso.

Em todas as views estamos usando os serializers e a injeção de dependência.

Apesar de termos criados as funções, o FastAPI ainda não sabe disso, o próximo passo será fazer o roteamento de URL -->
