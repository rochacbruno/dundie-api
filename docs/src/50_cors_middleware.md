# Middleware e CORS

## 1 Request -> REsponse

A parte mais importante de uma aplicação web é o fluxo de requisição,
ou seja, o cliente (browser) faz uma requisição (Request) ao servidor.

A requisição formatada no protocolo HTTP é enviada ao Servidor,
que por sua vez processa os elementos como URL, Verbo, Headers, Payload.

O servidor então prepara a resposta (Response) também no formato HTTP, contendo
HEADERS e Body e envia esta resposta ao cliente.


No FastAPI podemos inspecionar o objecto request, e modificar o objeto REsponse de maneira bastante simples.


Adicione em dundie/routes/user.py logo antes da rota list_users.

```python
@router.get("/test")
async def test_view(request: Request, response: Response):

    print(request.headers)
    print(response.headers)
    response.headers["X-Qualquer-Coisa"] = "123"
    return {}
```

Acesse http://localhost:8000/docs#/user/test_view_user_test_get e faça uma requisição.

repare que no terminal será impresso os valores dos headers, e no retorno da API no browser você verá o seu novo header `x-qualquer-coisa`.

Existem vários motivos para querermos injetar novos headers no objeto reponse,
ou inspecionar atributos do objeto request.

Um deles é para lidar com o conceito de CORS que já veremos a seguir.

Injetar headers HTTP individualmente em cada rota assim como fizemos acima as vezes é útil, agora imagine que precisamos injetar esse header em todas as rotas!

Seria preciso alterar código em muitos lugares, portanto podemos automizar com o uso de middlewares.


## Middleware

A palavra middleware pode significar coisas diferentes dependendo do tipo de software que estiver trabalhando, mas no contexto de aplicações web um middleware geralmente se refere a um procedimento que será **injetado** entre
o recebimento do Request e o envio do Response.


No fastapi podemos adicionar um middleware de duas formas, usando um decorator, ou adicionando explicitamente.

### Decorator

Começamos definindo uma função que irá receber o request e um callback para gerar o response.

No final do arquivo `app.py`

```python
@app.middleware("http")
async def add_new_header(request: Request, make_response):
    response = await make_response(request)
    response.headers["X-Qualquer-Coisa"] = "456"
    return response
```

Agora pode requisitar qualquer endpoint em http://localhost:8000/docs#/ que o novo será adicionado a todos.

Existem uma série de middlewares que podem ser adicionados para diversos fins, como por exemplo, redirecionar todos os usuários para uma determinada URL ou Schema, forçar a autenticação em um SSO etc.

### CORS

Este é o Middleware que com certeza qualquer aplicação com front-end irá necessitar, vamos antes entender o que é CORS.

Cross Origin Resource Sharing = Compartilhamento de Recursos entre Origens.

Recurso = URL/endpoint
Origin = Request principal iniciado pelo navegador


Bloqueio de compartilhamento entre origens é uma prática de segurança que é implementada em todos os principais navegadores.

Este bloqueio regula que, uma página web (pagina.html) quando for requisitada
só poderá requisitar novos recursos (outros endpoints) se este estiver na mesma origin, ou seja, no mesmo `schema:dominio:porta`.

PAra ver como isso funciona na prática vamos criar uma página em nossa `ui`

`ui/users.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Users</title>
</head>
<body>
<h1>Users List</h1>
<ul id="users-list"></ul>

<script>
// Function to create and append a new <li> element to the list
function appendUserToList(user) {
    var transactionList = document.getElementById("users-list");
    var listItem = document.createElement("li");
    listItem.textContent = user.name;
    transactionList.appendChild(listItem);
}

// Fetch API user list
fetch("http://localhost:8000/user/")
// parse to JSON
.then(response => response.json())
// loop the list and pass each user to the append function
.then(users => {
    users.forEach(user => {
        appendUserToList(user);
    });
});
</script>
</body>
</html>
```

Acesse no navegador http://localhost:8001/users.html e abra o console de dev (botao direito -> inspect) e na aba console veja o seguinte erro:

```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at http://localhost:8000/user/. (Reason: CORS header ‘Access-Control-Allow-Origin’ does not match ‘localhost:8001’).
```

Como a mensagem explica, a UI está sendo servida em `localhost:8001` e a API que queremos acessar está em `localhost:8000`, logo são consideradas origens diferentes.

Para resolver este problema precisamos dizer ao navegador que confiamos nessa comunicação.

Vamos fazer isso em nosso middleware, altere o middleware em `app.py`


```python
@app.middleware("http")
async def add_new_header(request: Request, make_response):
    response = await make_response(request)
    response.headers["X-Qualquer-Coisa"] = "456"
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8001"
    return response
```

Agora acesse http://localhost:8001/users.html e veja que dessa funcionou sem problemas.


### mais de uma origem?

Existem casos em que a app front-end precisa acessar recursos de mais de uma origem diferente,
porém o header `Access-Control-Allow-Origin` só aceita um único valor.

Neste caso será necessário uma implementação mais elaborada envolvendo expressões regulares para fazer o match em multiplas origens ou um esquema onde a origem em questão é resolvida em um request **pre-flight** que é quando o navegador envia um request `OPTIONS` perguntando ao
servidor se pode efetuar um request.

Uma opção também é usar o wildcard `*` para fazer match com qualquer origem, mas esta opção não é considerada segura e é usada apenas em APIs que são acessadas apenas em redes controladas.

O FastAPI tem uma forma mais sucinta de resolver este problema.


### Cors Middleware


Podemos agora comentar o nosso middleware do `app.py`, deixaremos o código comentado apenas como referencia.

```python
# @app.middleware("http")
# async def add_new_header(request: Request, make_response):
#     response = await make_response(request)
#     response.headers["X-Qualquer-Coisa"] = "456"
#     response.headers["Access-Control-Allow-Origin"] = "http://localhost:8001"
#     return response
```

Vamos usar então um middleware já embutido no FastAPI, no mesmo arquivo `app.py`


```python
from fastapi.middleware.cors import CORSMiddleware
...
# após `app= FastAPI(..)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://localhost",
        "https://server.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Este middleware irá automatizar uma série de coisas, fazendo a negociação inicial em **pre-flight** para construir o valor correto que vai no header
`"Access-Control-Allow-Origin"` e cuidando de configurações adicionais como decidir se esse header ser a adicionado para todos os métodos, se a parte de autenticação será incluida etc..

Tudo o que teriamos que fazer manualmente resolvido com um Middleware.

https://fastapi.tiangolo.com/tutorial/cors/


Ahh agora ao acessar http://localhost:8001/users.html tudo deve funcionar perfeitamente.






