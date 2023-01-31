# Update User

Agora vamos adicionar uma rota para que o usuário possa alterar o próprio perfil.

O usuário será capaz de mudar apenas os campos `bio` e `avatar`  
bio será um texto e avatar a URL de uma imagem, e é claro, o usuário só
poderá alterar o seu próprio perfil.

Vamos começar criando o serializer que irá receber essas informações a serem alteradas:

**EDITE** `models/user.py` e adicione:

```python
class UserProfilePatchRequest(BaseModel):
    avatar: Optional[str] = None
    bio: Optional[str] = None
```

E agora **EDITE** `routes/user.py` e adicione ao final.

```python
@router.patch("/{username}/", response_model=UserResponse)
async def update_user(
    *,
    session: Session = ActiveSession,
    patch_data: UserProfilePatchRequest,
    current_user: User = AuthenticatedUser,
    username: str
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # Update
    user.avatar = patch_data.avatar
    user.bio = patch_data.bio

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

Agora podemos testar a rota fazendo a alteração do perfil do usuário michael-scott, lembre-se que primeiro
será necessário obter um token válido com uma chamada na rota `/token`

```bash
curl -X 'PATCH' \
 -H 'Authorization: Bearer ...' \
 -H 'Content-Type: application/json' 
 --data-raw '{"avatar": "https://test.com/MichaelScott.png", "bio": "I am the boss"}' \
 -k 'http://localhost:8000/user/michael-scott/'
```

O usuário também precisará alterar a senha caso ele esqueça, vamos implementar esta funcionalidade -->
