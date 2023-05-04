# Esqueci minha senha

O próximo passo para completar a gestão de usuários é criarmos uma URL onde o usuário irá informar o seu `email` e o sistema vai verificar se existe um usuário com este e-mail cadastrado e então enviar um e-mail com o token para permitir a alteração de senha.

Nós já temos uma função que é capaz de gerar um token em `dundie/auth.py` chamada `create_access_token`

E vamos usar esta função para gerar o token de alteração de senha.

O fluxo será o seguinte:

01. Usuário requisita um token de senha em 
:
```http
POST /user/pwd_reset_token/

{
  "email": "michael-scott@dm.com"
}
```
```http
Response: 200 Ok
"Email will be sent if user is registered"
```

02. A view roteada em `/user/pwd_reset_token` vai fazer o seguinte:

- Invocar a função: `try_to_send_pwd_reset_email(email)`.

03. A função `try_to_send_pwd_reset_email` irá fazer o seguinte:

1. Procurar o usuário pelo e-mail
2. Criar um token com expiração curta (o tempo de expiração será definido nos settings)
3. Renderizar um template com o link para redefinir senha
4. Enviar o e-mail

## Enviando Email

Vamos começar criando uma função que irá receber alguns parametros e enviar um e-mail, 
teremos uma versão da função que de fato envia um e-mail via HTTP, e teremos outra
que apenas escreve a mensagem em um arquivo de log simulando o envio de e-mail que será
útil para testes.

**EDITE** `dundie/tasks/user.py`

```python
import smtplib
from datetime import timedelta
from time import sleep

from sqlmodel import Session, select

from dundie.auth import create_access_token
from dundie.config import settings
from dundie.db import engine
from dundie.models.user import User


def send_email(email: str, message: str):
    if settings.email.debug_mode is True:  # pyright: ignore
        _send_email_debug(email, message)
    else:
        _send_email_smtp(email, message)


def _send_email_debug(email: str, message: str):
    """Mock email sending by printing to a file"""
    with open("email.log", "a") as f:
        sleep(3)  # pretend it takes 3 seconds
        f.write(f"--- START EMAIL {email} ---\n" f"{message}\n" "--- END OF EMAIL ---\n")


def _send_email_smtp(email: str, message: str):
    """Connect to SMTP server and send email"""
    with smtplib.SMTP_SSL(
        settings.email.smtp_server, settings.email.smtp_port  # pyright: ignore  # pyright: ignore
    ) as server:
        server.login(settings.email.smtp_user, settings.email.smtp_password)  # pyright: ignore
        server.sendmail(
            settings.email.smtp_sender,  # pyright: ignore
            email,
            message.encode("utf8"),
        )


MESSAGE = """\
From: Dundie <{sender}>
To: {to}
Subject: Password reset for Dundie

Please use the following link to reset your password:
{url}?pwd_reset_token={pwd_reset_token}

This link will expire in {expire} minutes.
"""

def try_to_send_pwd_reset_email(email):
    """Given an email address sends email if user is found"""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            return

        sender = settings.email.smtp_sender  # pyright: ignore
        url = settings.security.PWD_RESET_URL  # pyright: ignore
        expire = settings.security.RESET_TOKEN_EXPIRE_MINUTES  # pyright: ignore

        pwd_reset_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=expire),  # pyright: ignore
            scope="pwd_reset",
        )

        send_email(
            email=user.email,
            message=MESSAGE.format(
                sender=sender,
                to=user.email,
                url=url,
                pwd_reset_token=pwd_reset_token,
                expire=expire,
            ),
        )
```


O próximo passo é editar o arquivo `dundie/default.toml` e adicionar os settings necessários para o serviço de emails.

```toml
[default.security]
...
RESET_TOKEN_EXPIRE_MINUTES = 10
PWD_RESET_URL = "https://dm.com/reset_password"

[default.email]
debug_mode = true
smtp_sender = "no-reply@dm.com"
smtp_server = "localhost"
smtp_port = 1025
smtp_user = "<replace in .secrets.toml>"
smtp_password = "<replace in .secrets.toml>"
```

Agora podemos abrir um terminal e testar essas funções

```python
$ docker compose exec api dundie shell

Auto imports: ['settings', 'engine', 'select', 'session', 'User']

In [1]: from dundie.tasks.user import try_to_send_pwd_reset_email

In [2]: try_to_send_pwd_reset_email("mscott@dm.com")  # wait 3 seconds

In [3]: open("email.log").readlines()
Out[3]: 
['--- START EMAIL mscott@dm.com ---\n',
 'From: Dundie <no-reply@dm.com>\n',
 'To: mscott@dm.com\n',
 'Subject: Password reset for Dundie\n',
 '\n',
 'Please use the following link to reset your password:\n',
 'https://dm.com/reset_password?pwd_reset_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsLXNjb3R0IiwiZXhwIjoxNjcyNjc3OTk1LCJzY29wZSI6InB3ZF9yZXNldCJ9.nAZNxHYniofTSCzBh38gPi5Qd0FoKONw1Ge6Yp40l5s\n',
 '\n',
 'This link will expire in 10 minutes.\n',
 '\n',
 '--- END OF EMAIL ---\n']
```

Cada e-mail enviado será adicionado ao arquivo email.log enquanto `settings.email.debug_mode` estiver ativado, futuramente podemos colocar os dados de um servidor smtp de verdade.

Agora a parte principal é criar uma rota que permitirá ao usuário solicitar o token de alteração de senha e disparar a task em background para o envio do e-mail.

**EDITE** `dundie/routes/user.py` e no final vamos adicionar.


```python
# import
from dundie.tasks.user import try_to_send_pwd_reset_email


# view
@router.post("/pwd_reset_token/")
async def send_password_reset_token(*, email: str = Body(embed=True)):
    """Sends an email with the token to reset password."""
    try_to_send_pwd_reset_email(email)
    return {
        "message": "If we found a user with that email, we sent a password reset token to it."
    }
```

```admonish tip "DICA"
Neste endpoint estamos recebendo `email` apenas no corpo do request, ao invés de criarmos um
serializer apenas para armazenar esta informação podemos usar o serializer genérico `Body` que
permite receber o valor de um campo diretamente no corpo do request.

No caso de um endereço de em-mail pode ser interessante criar um serializer para efetuar a 
verificando que o e-mail é valido, mas isso fica como melhoria para depois.
```

Testando:

```bash
curl -X 'POST' -H 'Content-Type: application/json' \
--data-raw '{"email": "mscott@dm.com"}' -k \
'http://localhost:8000/user/pwd_reset_token/'
```

```http
POST http://localhost:8000/user/pwd_reset_token/
#+END
HTTP/1.1 200 OK
date: Mon, 02 Jan 2023 16:42:56 GMT
server: uvicorn
content-length: 87
content-type: application/json

#+RESPONSE
{
  "message": "If we found a user with that email, we sent a password reset token to it."
}
#+END
```

Você pode agora verificar o conteúdo do arquivo `email.log` para ver se a mensagem foi realmente enviada.

```bash
$ cat email.log
...
```

```admonish todo "Tarefa"
No arquivo `dundie/tasks/user.py` estamos criando uma string `MESSAGE` para usar como template para o e-mail enviado,
mas seria ideal salvar essa string em um arquivo separado, por exemplo `pwd_reset_email_template.jinja`
e então usar o `jinja2` para renderizar o template, lembre-se que usamos o Jinja2 no Day1 do treinamento.

Consegue fazer esta alteração?
```

---

```admonish note "NOTA"
Por questões de privacidade nós não podemos confirmar se a operação deu certo, o usuário terá que verificar na caixa de e-mail que em nosso caso é o arquivo de log.
```

Mas repare que ao chamar a URL precisamos esperar 3 segundos pela resposta, o ideal é que o request seja imediato e a função
`taks.try_to_send_pwd_reset_email` seja executada em background. -->


