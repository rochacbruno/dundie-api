# Criando uma API base

Vamos editar o arquivo `dundie/app.py` e colocar a minima aplicação FastAPI 
só para que possamos rodar o container e testar se tudo está funcionando.

`dundie/app.py`
```python
from fastapi import FastAPI

app = FastAPI(
    title="dundie",
    version="0.1.0",
    description="dundie is a rewards API",
)
```

Salve as alterações e agora vamos partir para a definição do container ->
